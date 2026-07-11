from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .models import PetReport, UserProfile, LostPet, AdoptionRequest, PetClaimRequest
from django.contrib.admin.views.decorators import staff_member_required
from .forms import PetReportForm
from urllib.parse import quote
from django.utils import timezone
from datetime import timedelta
from datetime import datetime
from .models import ChatRoom, ChatRoomParticipant, ChatMessage

# ===================== PUBLIC HOME =====================

def public_home(request):
    pet_filter = request.GET.get("filter", "all")
    cutoff = timezone.now().date() - timedelta(days=15)

    if pet_filter == "lost":
        pets = LostPet.objects.filter(status="Approved")

    elif pet_filter == "found":
        pets = PetReport.objects.filter(
            report_type="Found",
            status="Approved",
            found_date__isnull=False,
            found_date__gt=cutoff
        )

    elif pet_filter == "adopt":
        pets = PetReport.objects.filter(
            report_type="Found",
            status="Approved",
            is_claimed=False,
            found_date__isnull=False,
            found_date__lte=cutoff
        )

    else:
        # 🚨 DJONGO SAFE DEFAULT
        pets = []

    return render(request, "public_home.html", {
        "pets": pets,
        "filter": pet_filter,
    })




# ===================== LOGIN =====================
def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            return render(request, "login.html", {"error": "Invalid email or password"})

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("admin_dashboard") if user.is_staff else redirect("dashboard")

        return render(request, "login.html", {"error": "Invalid email or password"})

    return render(request, "login.html")


# ===================== SIGNUP =====================



def signup(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        fullname = request.POST.get("fullname", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        age = request.POST.get("age")
        gender = request.POST.get("gender", "").strip()
        country = request.POST.get("country", "").strip()
        state = request.POST.get("state", "").strip()
        district = request.POST.get("district", "").strip()
        pincode = request.POST.get("pincode", "").strip()
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        # ---------- VALIDATIONS ----------
        if not username or not fullname or not email:
            return render(request, "signup.html", {
                "error": "Username, Full Name and Email are required"
            })

        if password != confirm:
            return render(request, "signup.html", {
                "error": "Passwords do not match"
            })

        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {
                "error": "Username already exists"
            })

        if User.objects.filter(email=email).exists():
            return render(request, "signup.html", {
                "error": "Email already exists"
            })

        # ---------- CREATE USER ----------
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=fullname
        )

        # ---------- CREATE PROFILE ----------
        UserProfile.objects.create(
            user=user,
            full_name=fullname,
            phone=phone or None,
            age=int(age) if age else None,
            gender=gender or None,
            country=country or None,
            state=state or None,
            district=district or None,
            pincode=pincode or None
        )

        login(request, user)
        return redirect("dashboard")

    return render(request, "signup.html")


# ===================== DASHBOARD =====================


@login_required
def dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    pet_filter = request.GET.get("filter", "all")
    cutoff = timezone.now().date() - timedelta(days=15)

    lost_pets = LostPet.objects.filter(status="Approved")
    found_qs = PetReport.objects.filter(
        report_type="Found",
        status="Approved",
        found_date__isnull=False
    )

    active_found = []
    adoptable_pets = []

    # Normalize LostPets
    for pet in lost_pets:
        pet.is_adoption = False

    # Normalize FoundPets
    for pet in found_qs:
        pet.is_adoption = False
        if pet.found_date <= cutoff and not pet.is_claimed:
            pet.is_adoption = True
            adoptable_pets.append(pet)
        else:
            active_found.append(pet)

    if pet_filter == "lost":
        pets = lost_pets
    elif pet_filter == "found":
        pets = active_found
    elif pet_filter == "adopt":
        pets = adoptable_pets
    else:
        pets = list(lost_pets) + active_found + adoptable_pets
    

     # whatever you already have
    
    pet_name = request.GET.get("pet_name")
    species = request.GET.get("species")
    breed = request.GET.get("breed")
    location = request.GET.get("location")


    if pet_name:
        pets = [
            p for p in pets
            if hasattr(p, "pet_name")
            and p.pet_name
            and pet_name.lower() in p.pet_name.lower()
        ]
    if species:
        pets = [
            p for p in pets
            if (
                (hasattr(p, "species") and p.species and species.lower() in p.species.lower())
                or
                (hasattr(p, "pet_type") and p.pet_type and species.lower() in p.pet_type.lower())
            )
        ]



    if breed:
        pets = [p for p in pets if p.breed and breed.lower() in p.breed.lower()]

    if location:
        pets = [p for p in pets if p.location and location.lower() in p.location.lower()]


    search_done = any([pet_name, species, breed, location])

    if search_done:
        if pets:
            messages.success(request, "✅ Matching pet records found.")
        else:
            messages.warning(request, "❌ No matching pet records found.")

    return render(request, "dashboard.html", {
        "profile": profile,
        "pets": pets,
        "filter": pet_filter,
    })



# ===================== PROFILE =====================
@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "full_name": request.user.first_name or request.user.username,
            "phone": "",
            "age": None,
            "gender": "",
            "country": "",
            "state": "",
            "district": "",
            "pincode": "",
        }
    )
    return render(request, "profile.html", {
        "user": request.user,
        "profile": profile
    })



# ===================== REPORT LOST PET (1st COPY) =====================
# ===================== REPORT LOST PET =====================

@login_required
def report_lost_pet(request):
    if request.method == "POST":

        pet_name = request.POST.get("pet_name")
        pet_type = request.POST.get("pet_type")
        breed = request.POST.get("breed")
        color = request.POST.get("color")
        age = request.POST.get("age")
        gender = request.POST.get("gender")
        lost_date = request.POST.get("lost_date")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        location = request.POST.get("location")
        raw_location_url = request.POST.get("location_url", "").strip()  # (updated)
        vaccinated = request.POST.get("vaccinated")
        weight = request.POST.get("weight")
        health_status = request.POST.get("health_status")
        description = request.POST.get("description")
        pet_image = request.FILES.get("pet_image")
        owner_name = request.POST.get("owner_name", "").strip()

        if not owner_name:
            owner_name = request.user.get_full_name() or request.user.username



        if not (pet_name and pet_type and lost_date and phone and location):
            messages.error(request, "Please fill all required fields.")
            return redirect("report_lost_pet")

        # 🔥 AUTO-CONVERT map link logic
        if raw_location_url:
            # Case 1 → user typed address name (not a URL)
            if not raw_location_url.startswith("http://") and not raw_location_url.startswith("https://"):
                from urllib.parse import quote
                location_url = f"https://www.google.com/maps?q={quote(raw_location_url)}"
            else:
                location_url = raw_location_url  # user pasted correct URL
        else:
            # Case 2 → URL empty → fallback to typed location
            from urllib.parse import quote
            location_url = f"https://www.google.com/maps?q={quote(location)}"

        # 🔥 Saving
        LostPet.objects.create(
            user=request.user,
            pet_name=pet_name,
            pet_type=pet_type,
            breed=breed,
            color=color,
            age=age,
            owner_name=owner_name,
            gender=gender,
            lost_date=lost_date,
            phone=phone,
            email=email,
            location=location,
            location_url=location_url,
            description=description,
            vaccinated=vaccinated,     
            weight=weight,               # <-- added
            health_status=health_status,
            pet_image=pet_image
        )

        messages.success(request, "✔ Lost Pet Report Submitted Successfully!")
        return redirect("dashboard")

    return render(request, "report_lost_pet.html")


# ===================== REPORT LOST PET (2nd COPY - Duplicate) =====================
# ===================== REPORT FOUND PET =====================

@login_required
def report_found_pet(request):
    if request.method == "POST":

        # Fetching all form fields manually (matching your HTML form)
        
        species = request.POST.get("species")
        breed = request.POST.get("breed")
        color = request.POST.get("color")
        age = request.POST.get("age")
        gender = request.POST.get("gender")
        weight = request.POST.get("weight")
        health_status = request.POST.get("health_status")
        found_date_str = request.POST.get("found_date")
        found_date = datetime.strptime(found_date_str, "%Y-%m-%d").date()
        found_time = request.POST.get("found_time")
        contact_number = request.POST.get("contact_number")
        contact_email = request.POST.get("contact_email")
        location = request.POST.get("location")
        raw_location_url = request.POST.get("location_url", "").strip()
        description = request.POST.get("description")
        image = request.FILES.get("image")
        owner_name = request.POST.get("owner_name", "").strip()

        if not owner_name:
            owner_name = request.user.get_full_name() or request.user.username



        # ⭐ Auto map conversion
        from urllib.parse import quote
        if raw_location_url:
            if not raw_location_url.startswith("http"):
                location_url = f"https://www.google.com/maps?q={quote(raw_location_url)}"
            else:
                location_url = raw_location_url
        else:
            location_url = f"https://www.google.com/maps?q={quote(location)}"

        # ⭐ SAVE — no duplication now
        PetReport.objects.create(
            user=request.user,
            species=species,
            breed=breed,
            color=color,
            age=age,
            gender=gender,
            found_date=found_date,
            found_time=found_time,
            weight=weight,               # <-- added
            health_status=health_status, # <-
            contact_number=contact_number,
            contact_email=contact_email,
            location=location,
            location_url=location_url,
            description=description,
            image=image,
            owner_name=owner_name, 
            report_type="Found",
            status="Pending"
        )

        messages.success(request, "✔ Found Pet Report Submitted Successfully!")
        return redirect("dashboard")

    return render(request, "report_found_pet.html")


# ===================== CHANGE PASSWORD =====================
def change_password(request):
    if request.method == "POST":
        old = request.POST.get("old_password")
        new = request.POST.get("new_password")
        conf = request.POST.get("confirm_password")

        if not request.user.check_password(old):
            messages.error(request, "❌ Old password incorrect")
            return redirect("change_password")

        if new != conf:
            messages.error(request, "❌ Passwords don't match")
            return redirect("change_password")

        request.user.set_password(new)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "✔ Password Updated Successfully")
        return redirect("profile")

    return render(request, "change_password.html")


# ===================== ADMIN DASHBOARD =====================

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):

    # ===== TOP SUMMARY (UNCHANGED) =====
    total_users = User.objects.count()

    total_pets = (
        LostPet.objects.filter(status="Approved").count() +
        PetReport.objects.filter(report_type="Found", status="Approved").count() +
        AdoptionRequest.objects.filter(status="Approved").count()
    )

    pending_reports = (
        LostPet.objects.filter(status="Pending").count() +
        PetReport.objects.filter(report_type="Found", status="Pending").count() +
        AdoptionRequest.objects.filter(status="Pending").count()
    )

    # ===== PETS OVERVIEW (APPROVED ONLY) =====
    approved_lost_pets = LostPet.objects.filter(status="Approved").count()

    approved_found_pets = PetReport.objects.filter(
        report_type="Found",
        status="Approved"
    ).count()

    approved_adoption_pets = AdoptionRequest.objects.filter(
        status="Approved"
    ).count()

    # ===== RESOLVED CASES =====
    resolved_cases = (
    LostPet.objects.filter(status="Approved").count() +
    AdoptionRequest.objects.filter(status="Approved").count()
)


    return render(request, "admin_dashboard.html", {
        "total_users": total_users,
        "total_pets": total_pets,
        "pending_reports": pending_reports,

        # 👇 NEW (Pets Overview)
        "approved_lost_pets": approved_lost_pets,
        "approved_found_pets": approved_found_pets,
        "approved_adoption_pets": approved_adoption_pets,

        "resolved_cases": resolved_cases,
    })



# ===================== ADMIN REPORT LIST =====================
@user_passes_test(lambda u: u.is_staff)
def admin_reports(request):
    pending_lost = LostPet.objects.filter(status="Pending")
    pending_found = PetReport.objects.filter(report_type="Found", status="Pending")
    return render(request, "admin_reports.html", {
        "pending_lost": pending_lost,
        "pending_found": pending_found
    })



# ===================== ADMIN – FOUND REQUESTS =====================
@user_passes_test(lambda u: u.is_staff)
def admin_found_requests(request):
    if request.method == "POST":
        report_id = request.POST.get("id")
        action = request.POST.get("action")

        pet = get_object_or_404(PetReport, id=report_id, report_type="Found")
        pet.status = "Approved" if action == "Approved" else "Rejected"
        pet.save()
        return redirect("admin_found_requests")

    reports = PetReport.objects.filter(report_type="Found", status="Pending").order_by("-found_date")
    return render(request, "admin_found_requests.html", {"reports": reports})


# ===================== UPDATE STATUS =====================

def update_report_status(request, report_id, action):
    pet = get_object_or_404(PetReport, id=report_id)
    action = action.capitalize()

    if action == "Approve":
        pet.status = "Approved"
        pet.save()

    elif action == "Reject":
        pet.status = "Rejected"
        pet.save()

    return redirect("admin_pending_tasks")


# ===================== ADMIN USERS =====================
@user_passes_test(lambda u: u.is_staff)
def admin_users(request):
    users = User.objects.all().order_by("-date_joined")
    return render(request, "admin_users.html", {"users": users})


# ===================== ADMIN SIGNUP =====================
def admin_signup(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")
        admin_secret = request.POST.get("admin_secret")

        from django.conf import settings
        if admin_secret != settings.ADMIN_SECRET_KEY:
            return render(request, "signup.html", {"admin_error": "Invalid Admin Secret Key"})

        if password != confirm:
            return render(request, "signup.html", {"admin_error": "Passwords do not match"})

        if User.objects.filter(email=email).exists():
            return render(request, "signup.html", {"admin_error": "Email already exists"})

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=fullname,
            is_staff=True
        )
        UserProfile.objects.create(user=user, full_name=fullname)
        login(request, user)
        return redirect("admin_dashboard")

    return render(request, "admin_register.html")


# ===================== PET DETAILS =====================


def pet_details(request, pet_type, pet_id):

    if pet_type == "lost":
        pet = get_object_or_404(LostPet, pk=pet_id)

    elif pet_type == "found":
        pet = get_object_or_404(PetReport, pk=pet_id)

    elif pet_type == "adopt":
        pet = get_object_or_404(PetReport, pk=pet_id)


    return render(request, "pet_details.html", {
        "pet": pet,
        "pet_type": pet_type,
    })


# ===================== LOST PET FORM =====================

# ===================== ADMIN – LOST REQUESTS =====================


@user_passes_test(lambda u: u.is_staff)
def admin_lost_requests(request):
    reports = LostPet.objects.filter(status="Pending")  # reads correct table
    return render(request, "admin_lost_requests.html", {"reports": reports})
 
@user_passes_test(lambda u: u.is_staff)
def update_lost_status(request, report_id, action):
    pet = get_object_or_404(LostPet, id=report_id)

    if action == "approve":
        pet.status = "Approved"
        pet.save()

    else:  # REJECT
        pet.status = "Rejected"
        pet.save()
 # ❗ removed from database immediately

    return redirect("admin_pending_tasks")



# Adoption request
@login_required
def adopt_request(request, pet_id):
    pet = get_object_or_404(
        PetReport,
        id=pet_id,
        status="Approved",
        report_type="Found"
    )
    if AdoptionRequest.objects.filter(user=request.user, pet=pet).exists():
        messages.warning(request, "⚠ You have already requested adoption for this pet.")
        return redirect("dashboard")
    AdoptionRequest.objects.create(
        user=request.user,
        pet=pet
    )

    messages.success(request, "🐾 Adoption request sent.")
    return redirect("dashboard")

def get_eligible_for_adoption():
    cutoff_date = timezone.now().date() - timedelta(days=15)

    return PetReport.objects.filter(
        report_type="Found",
        status="Approved",
        is_claimed=False,
        found_date__isnull=False,
        found_date__lte=cutoff_date,
    )



@user_passes_test(lambda u: u.is_staff)
def approve_adoption(request, request_id):
    req = get_object_or_404(AdoptionRequest, id=request_id)
    req.status = "Approved"
    req.save()

    pet = req.pet
    pet.is_claimed = True   # ✅ THIS is the adoption flag
    pet.save()

    AdoptionRequest.objects.filter(
        pet=pet,
        status="Pending"
    ).exclude(id=req.id).delete()

    messages.success(request, "Adoption approved. Case closed.")
    return redirect("admin_pending_tasks")




@user_passes_test(lambda u: u.is_staff)
def reject_adoption(request, request_id):
    req = get_object_or_404(AdoptionRequest, id=request_id)
    req.delete()  # ✅ IMPORTANT
    messages.success(request, "Adoption request rejected.")
    return redirect("admin_pending_tasks")



@login_required
def adopt_pet(request):
    return redirect('/dashboard/?filter=adopt#pets')


@user_passes_test(lambda u: u.is_staff)
def admin_adoption_requests(request):
    requests = AdoptionRequest.objects.filter(
        status="Pending",
        pet__isnull=False   # 🔥 IMPORTANT
    ).select_related("pet", "user")

    return render(request, "admin_adoption_requests.html", {
        "requests": requests
    })



@user_passes_test(lambda u: u.is_staff)
def admin_pending_tasks(request):
    req_type = request.GET.get("type", "all")

    pending = [] 

    # 1️⃣ Lost Pets
    lost_qs = LostPet.objects.filter(status="Pending")
    for obj in lost_qs:
        obj.item_type = "lost"
        pending.append(obj)

    # 2️⃣ Found Pets
    found_qs = PetReport.objects.filter(status="Pending", report_type="Found")
    for obj in found_qs:
        obj.item_type = "found"
        pending.append(obj)

    # 3️⃣ Adoption Requests (IMPORTANT FIX)
    adoption_qs = AdoptionRequest.objects.filter(status="Pending").select_related("pet")
    for obj in adoption_qs:
        obj.item_type = "adopt"
        pending.append(obj)

    # 🔍 FILTER BY TAB
    if req_type != "all":
        pending = [p for p in pending if p.item_type == req_type]

    return render(request, "admin_pending_tasks.html", {
        "pending": pending,
        "req_type": req_type,

        "lost_count": lost_qs.count(),
        "found_count": found_qs.count(),
        "adopt_count": adoption_qs.count(),



    })


@user_passes_test(lambda u: u.is_staff)
def approved_reports(request):
    pet_filter = request.GET.get("filter", "all")
    reports = []

    # 🔴 LOST (Approved)
    lost_qs = LostPet.objects.filter(status="Approved")
    for pet in lost_qs:
        pet.display_type = "lost"
        reports.append(pet)

    # 🔵 FOUND & 🟣 ADOPTED
    found_qs = PetReport.objects.filter(
        status="Approved",
        report_type="Found"
    )

    for pet in found_qs:
        if AdoptionRequest.objects.filter(
            pet=pet,
            status="Approved"
        ).exists():
            pet.display_type = "adopted"
        else:
            pet.display_type = "found"

        reports.append(pet)

    # 🔍 APPLY FILTER
    if pet_filter != "all":
        reports = [r for r in reports if r.display_type == pet_filter]

    return render(request, "approved_reports.html", {
        "reports": reports,
        "filter": pet_filter,
    })



@login_required
def search_found_pets(request):
    pets = PetReport.objects.filter(
        report_type="Found",
        status="Approved"
    )

    pet_type = request.GET.get("pet_type")
    breed = request.GET.get("breed")
    location = request.GET.get("location")

    if pet_type:
        pets = pets.filter(pet_type__icontains=pet_type)
    if breed:
        pets = pets.filter(breed__icontains=breed)
    if location:
        pets = pets.filter(location__icontains=location)

    return render(
        request,
        "dashboard/search_found_pets.html",
        {"pets": pets}
    )


@staff_member_required
def admin_user_details(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = UserProfile.objects.filter(user=user).first()

    return render(request, "admin_user_details.html", {
        "user_obj": user,
        "profile": profile
    })


@staff_member_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # ❗ Safety: prevent admin deleting themselves
    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect("admin_user_details", user_id=user.id)

    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect("admin_users")



@login_required
def send_claim_request(request, pet_type, pet_id):
    if request.method != "POST":
        return redirect("dashboard")

    if pet_type == "lost":
        pet = get_object_or_404(LostPet, id=pet_id)

        existing = PetClaimRequest.objects.filter(
            requester=request.user,
            request_type="lost",
            lost_pet=pet,
            status="Pending"
        ).exists()

        if existing:
            messages.warning(request, "⚠ You already sent a request for this pet.")
            return redirect("dashboard")

        PetClaimRequest.objects.create(
            request_type="lost",
            lost_pet=pet,
            requester=request.user,
            message=request.POST.get("message", "")
        )

    elif pet_type == "found":
        pet = get_object_or_404(PetReport, id=pet_id)

        existing = PetClaimRequest.objects.filter(
            requester=request.user,
            request_type="found",
            found_pet=pet,
            status="Pending"
        ).exists()

        if existing:
            messages.warning(request, "⚠ You already sent a request for this pet.")
            return redirect("dashboard")

        PetClaimRequest.objects.create(
            request_type="found",
            found_pet=pet,
            requester=request.user,
            message=request.POST.get("message", "")
        )

    messages.success(
        request,
        "📩 Request sent to admin. You will be notified after verification."
    )
    return redirect("dashboard")


@user_passes_test(lambda u: u.is_staff)
def admin_chat_requests(request):
    requests = PetClaimRequest.objects.all().order_by("-created_on")

    for r in requests:
        try:
            chatroom = ChatRoom.objects.get(claim_request_id=r.id)
            r.chat_status = chatroom.status or "OPEN"
        except ChatRoom.DoesNotExist:
            r.chat_status = None

    return render(request, "admin_chat_requests.html", {
        "requests": requests
    })




@user_passes_test(lambda u: u.is_staff)
def admin_chat_request_detail(request, request_id):
    req = get_object_or_404(PetClaimRequest, id=request_id)
    if req.status == "Approved":
        return redirect("chat_room", request_id=req.id)

    if req.request_type == "lost":
        pet = req.lost_pet
        pet_kind = "lost"
    else:
        pet = req.found_pet
        pet_kind = "found"

    context = {
        "req": req,
        "pet": pet,
        "pet_kind": pet_kind,
        "requester": req.requester,
        "reporter": pet.user if hasattr(pet, "user") else None,
    }
    return render(request, "admin_chat_request_detail.html", context)


# views.py


from .models import PetClaimRequest

from django.urls import reverse


@staff_member_required
def approve_chat_request(request, request_id):
    req = get_object_or_404(PetClaimRequest, id=request_id)

    # 1️⃣ Create / fetch chatroom (SAFE)
    chatroom = ChatRoom.objects.filter(
        claim_request_id=req.id
    ).first()

    if not chatroom:
        chatroom = ChatRoom.objects.create(
            claim_request_id=req.id,
            status="OPEN"
        )

    # 2️⃣ Approve request
    req.status = "Approved"
    req.save()

    # 3️⃣ Add admin safely
    admin_exists = ChatRoomParticipant.objects.filter(
        chatroom_id=chatroom.id,
        user_id=request.user.id,
        role="admin"
    ).first()

    if not admin_exists:
        ChatRoomParticipant.objects.create(
            chatroom_id=chatroom.id,
            user_id=request.user.id,
            role="admin"
        )

    # 4️⃣ Add requester safely
    requester_exists = ChatRoomParticipant.objects.filter(
        chatroom_id=chatroom.id,
        user_id=req.requester.id,
        role="requester"
    ).first()

    if not requester_exists:
        ChatRoomParticipant.objects.create(
            chatroom_id=chatroom.id,
            user_id=req.requester.id,
            role="requester"
        )

    messages.success(request, "Chat request approved successfully.")
    return redirect("chat_room", request_id=req.id)








@staff_member_required
def add_reporter(request, request_id):
    if request.method == "POST":
        chatroom = get_object_or_404(
            ChatRoom,
            claim_request_id=request_id
        )

        reporter_id = request.POST.get("reporter_id")
        reporter = get_object_or_404(User, id=reporter_id)

        ChatRoomParticipant.objects.get_or_create(
            chatroom_id=chatroom.id,
            user_id=reporter.id,
            role="reporter"
        )

    return redirect("chat_room", request_id=request_id)



@staff_member_required
def reject_chat_request(request, request_id):
    req = get_object_or_404(PetClaimRequest, id=request_id)
    req.delete()
    messages.success(request, "Chat request rejected and removed.")
    return redirect("admin_chat_requests")



@login_required
def chat_room(request, request_id):
    req = get_object_or_404(
        PetClaimRequest,
        id=request_id,
        status="Approved"
    )
    chatroom = get_object_or_404(
        ChatRoom,
        claim_request_id=req.id
    )

    # 🔥 ADMIN AUTO-SYNC (MANDATORY)
    if request.user.is_staff:
        ChatRoomParticipant.objects.get_or_create(
            chatroom_id=chatroom.id,
            user_id=request.user.id,
            role="admin"
        )

    # 🔐 ACCESS CHECK
    if not ChatRoomParticipant.objects.filter(
        chatroom_id=chatroom.id,
        user_id=request.user.id
    ).exists():
        messages.error(request, "Access denied.")
        return redirect("dashboard")

    # ❌ BLOCK SEND IF CLOSED
    if request.method == "POST":
        if chatroom.status == "CLOSED":
            messages.warning(request, "This chat is closed.")
            return redirect("chat_room", request_id=req.id)

        msg = request.POST.get("message", "").strip()
        image = request.FILES.get("image")

        print("FILES:", request.FILES)
        print("MSG:", msg)
        if not msg and not image:
            return redirect("chat_room", request_id=req.id)
        
        if msg and not image:
            ChatMessage.objects.create(
                chatroom_id=chatroom.id,
                sender_id=request.user.id,
                message=msg
        )
            return redirect("chat_room", request_id=req.id)

        
        chat_msg = ChatMessage(
            chatroom_id=chatroom.id,
            sender_id=request.user.id,
            message=msg or ""
    )
           # 🔴 FIRST SAVE (row creation)

        if image:
            chat_msg.image.save(image.name, image, save=True)
        
        return redirect("chat_room", request_id=req.id)

    # 🐾 PET CONTEXT
    if req.request_type == "lost":
        pet = req.lost_pet
        pet_kind = "lost"
        reporter = pet.user
    else:
        pet = req.found_pet
        pet_kind = "found"
        reporter = pet.user

    # 👥 PARTICIPANTS (ADMINS FIRST)
    # 👥 PARTICIPANTS (ADMINS FIRST, NO DUPLICATES)

    # 👥 PARTICIPANTS (STABLE ADMIN LABELS)
    

    participants = []

# 1️⃣ Get unique admin users (sorted by date_joined)
    admin_users = (
        User.objects
        .filter(
            id__in=ChatRoomParticipant.objects.filter(
                chatroom_id=chatroom.id,
                role="admin"
            ).values_list("user_id", flat=True)
        )
        .order_by("date_joined")
    )

    admin_label_map = {}
    for index, admin in enumerate(admin_users, start=1):
        admin_label_map[admin.id] = f"Admin{index}"

        p = ChatRoomParticipant.objects.filter(
            chatroom_id=chatroom.id,
            user_id=admin.id,
            role="admin"
        ).first()

        p.user = admin
        p.display_name = f"Admin{index}"
        participants.append(p)

# 2️⃣ Non-admin participants
    for p in ChatRoomParticipant.objects.filter(
        chatroom_id=chatroom.id
    ).exclude(role="admin"):
        p.user = User.objects.get(id=p.user_id)
        p.display_name = p.user.username
        participants.append(p)



    messages_list = ChatMessage.objects.filter(
        chatroom_id=chatroom.id
    ).order_by("created_at")

    for m in messages_list:
        m.sender = User.objects.get(id=m.sender_id)

        if m.sender.is_staff:
            m.sender_label = admin_label_map[m.sender.id]
        else:
            m.sender_label = m.sender.username



    template = (
        "chat_room_admin.html"
        if request.user.is_staff
        else "chat_room_user.html"
    )

    return render(request, template, {
        "req": req,
        "pet": pet,
        "pet_kind": pet_kind,
        "participants": participants,
        "messages": messages_list,
        "reporter": reporter,
        "chatroom": chatroom,
    })


@login_required
def user_chats(request):

    participants = list(
        ChatRoomParticipant.objects.filter(
            user_id=request.user.id
        ).order_by("-id")
    )

    # 🔹 Collect chatroom IDs in Python
    chatroom_ids = [p.chatroom_id for p in participants]

    # 🔹 DJONGO-SAFE unread count (NO __in, NO exclude)
    unread_count = 0
    for msg in ChatMessage.objects.all():
        if (
            msg.chatroom_id in chatroom_ids and
            not msg.is_read and
            msg.sender_id != request.user.id
        ):
            unread_count += 1

    rooms = []
    for p in participants:
        room = ChatRoom.objects.get(
            id=p.chatroom_id
        )

        # 🔹 get last message safely
        last_msg = None
        for m in ChatMessage.objects.filter(chatroom_id=p.chatroom_id):
            last_msg = m

        room.last_message = (
            last_msg.message if last_msg else "Admin-approved chat"
        )
        room.last_time = (
            last_msg.created_at if last_msg else room.created_at
        )

        rooms.append(room)

    return render(request, "user_chats.html", {
        "rooms": rooms,
        "unread_count": unread_count
    })





@staff_member_required
def close_chat(request, request_id):
    chatroom = get_object_or_404(ChatRoom, claim_request_id=request_id)

    chatroom.status = "CLOSED"
    chatroom.save()

    messages.success(request, "Chat closed. Case resolved.")
    return redirect("chat_room", request_id=request_id)

