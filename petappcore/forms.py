from django import forms
from .models import PetReport

class PetReportForm(forms.ModelForm):
    class Meta:
        model = PetReport
        fields = [
            'species', 'breed', 'color', 'age', 'gender', 'found_date',
            'contact_number', 'contact_email', 'location', 'location_url', 'description', 'image'
        ]
