from django.contrib import admin
from .models import PetReport,  LostPet

@admin.register(PetReport)
class PetReportAdmin(admin.ModelAdmin):

    # 🔥 Show actual fields your model contains
    list_display = (
        'species', 'breed', 'color', 'age', 'gender',
        'location', 'found_date', 'status', 'report_type'
    )

    list_filter = ('status', 'report_type', 'gender', 'color')
    search_fields = ('species', 'breed', 'location', 'contact_number')

    # Admin Actions
    actions = ['approve_report', 'reject_report']

    def approve_report(self, request, queryset):
        queryset.update(status='Approved')

    def reject_report(self, request, queryset):
        queryset.update(status='Rejected')

    approve_report.short_description = "Approve Selected Reports"
    reject_report.short_description = "Reject Selected Reports"




@admin.register(LostPet)
class LostPetAdmin(admin.ModelAdmin):
    list_display = ('pet_name', 'pet_type', 'color', 'age', 'gender', 'location', 'location_url', 'lost_date', 'status')
    search_fields = ('pet_name', 'location')
    list_filter = ('status', 'gender', 'color')
