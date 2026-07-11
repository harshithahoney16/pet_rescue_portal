print("🔵 LOADED convert_to_adoption.py")

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from petappcore.models import PetReport, AdoptPet

class Command(BaseCommand):
    help = "Convert eligible approved found pets to AdoptPet after 15 days"

    def handle(self, *args, **options):
        print("🔥 NEW ADOPTION COMMAND EXECUTING")

        cutoff_ts = (timezone.now() - timedelta(days=15)).timestamp()

        # Djongo-safe: no filtering using SQL
        all_pets = PetReport.objects.all()

        all_found = [
            pet for pet in all_pets
            if pet.report_type == "Found"
            and pet.status == "Approved"
            and not pet.is_claimed
        ]

        print(f"🔍 Found {len(all_found)} approved unclaimed found pets")

        candidates = [
            pet for pet in all_found
            if float(pet.created_on) <= cutoff_ts
        ]

        print(f"🎯 Eligible pets for adoption: {len(candidates)}")

        for pet in candidates:
            if getattr(pet, "source_report", None) and AdoptPet.objects.filter(source_report=pet).exists():
                print(f"⏩ Already converted: {pet.id}")
                continue

            AdoptPet.objects.create(
                pet_name = pet.pet_name or pet.species or "Unknown",
                species  = pet.species,
                breed    = pet.breed,
                color    = pet.color,
                age      = pet.age,
                gender   = pet.gender,
                description = pet.description,
                location = pet.location,
                image    = pet.image,
                source_report = pet
            )

            pet.status = "ConvertedToAdoption"
            pet.save()

            print(f"✅ Converted PetReport {pet.id}")

        print("✔ DONE")
