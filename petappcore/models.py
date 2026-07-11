from django.db import models
from django.contrib.auth.models import User


# ---------------------------------------
# MODEL 1: User Profile
# ---------------------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)

    country = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username


# ---------------------------------------
# MODEL 2: Lost / Found Pet Reports
# (Single source of truth)
# ---------------------------------------
class PetReport(models.Model):
    REPORT_TYPE_CHOICES = (
        ("Lost", "Lost"),
        ("Found", "Found"),
    )

    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Approved", "Approved"),   # Found OR Adoptable (decided by date)
        ("Rejected", "Rejected"),
        ("Adopted", "Adopted"),     # Final state
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)

    # Pet details
    pet_name = models.CharField(max_length=100, null=True, blank=True)
    species = models.CharField(max_length=50, null=True, blank=True)
    breed = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    age = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    weight = models.CharField(max_length=50, null=True, blank=True)
    health_status = models.CharField(max_length=200, null=True, blank=True)

    # Found-specific
    found_date = models.DateField(null=True, blank=True)
    found_time = models.TimeField(blank=True, null=True)

    # Contact & location
    contact_number = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    location = models.CharField(max_length=255)
    location_url = models.URLField(blank=True, null=True)
    owner_name = models.CharField(
    max_length=100,
    blank=True,
    null=True
)



    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to="pet_images/", null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    is_claimed = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.report_type} - {self.pet_name or self.species} ({self.status})"


# ---------------------------------------
# MODEL 3: Lost Pet (kept separate as you designed)
# ---------------------------------------
class LostPet(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    pet_name = models.CharField(max_length=100)
    pet_type = models.CharField(max_length=100)
    breed = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length=20)
    age = models.CharField(max_length=50, blank=True)
    vaccinated = models.CharField(max_length=10, null=True, blank=True)
    weight = models.CharField(max_length=50, null=True, blank=True)
    health_status = models.CharField(max_length=200, null=True, blank=True)
    owner_name = models.CharField(max_length=100, blank=True, null=True)



    lost_date = models.DateField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    location = models.CharField(max_length=200)
    location_url = models.URLField(blank=True, null=True, default="")
    description = models.TextField(blank=True)
    pet_image = models.ImageField(upload_to="lost_pets/", blank=True, null=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    reported_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.pet_name


# ---------------------------------------
# MODEL 4: Adoption Request
# ---------------------------------------
class AdoptionRequest(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pet = models.ForeignKey(PetReport, on_delete=models.CASCADE)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Adoption request by {self.user.username} for {self.pet.pet_name or self.pet.species}"

class PetClaimRequest(models.Model):
    REQUEST_TYPES = (
        ("lost", "Found Lost Pet"),
        ("found", "Claim Found Pet"),
    )

    request_type = models.CharField(
        max_length=20,
        choices=REQUEST_TYPES,
        default="found"
    )

    lost_pet = models.ForeignKey(
        LostPet, null=True, blank=True, on_delete=models.CASCADE
    )
    found_pet = models.ForeignKey(
        PetReport, null=True, blank=True, on_delete=models.CASCADE
    )

    requester = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True)

    status = models.CharField(
        max_length=10,
        choices=[("Pending","Pending"),("Approved","Approved"),("Rejected","Rejected")],
        default="Pending"
    )

    created_on = models.DateTimeField(auto_now_add=True)

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.request_type == "lost" and not self.lost_pet:
            raise ValidationError("Lost pet must be provided for lost request")

        if self.request_type == "found" and not self.found_pet:
            raise ValidationError("Found pet must be provided for found request")

        if self.lost_pet and self.found_pet:
            raise ValidationError("Only one pet reference is allowed")


# models.py


class ChatRoom(models.Model):
    claim_request_id = models.IntegerField(unique=True, db_index=True)
    status = models.CharField(
        max_length=10,
        choices=[("OPEN", "Open"), ("CLOSED", "Closed")],
        default="OPEN"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False   # 🚨 IMPORTANT for Djongo

    def __str__(self):
        return f"ChatRoom for Request {self.claim_request_id}"
    



class ChatRoomParticipant(models.Model):
    chatroom_id = models.IntegerField(db_index=True)
    user_id = models.IntegerField(db_index=True)
    role = models.CharField(max_length=20)

    class Meta:
        managed = False


class ChatMessage(models.Model):
    chatroom_id = models.IntegerField(db_index=True)
    sender_id = models.IntegerField(db_index=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="chat_images/", blank=True, null=True)
    is_read = models.BooleanField(default=False)
    class Meta:
        managed = False
        ordering = ["created_at"]

  
