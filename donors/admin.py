from django.contrib import admin
from .models import DonorProfile

class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'blood_group', 'city', 'phone_number', 'availability_status', 'is_eligible')
    list_filter = ('blood_group', 'city', 'availability_status')
    search_fields = ('full_name', 'city', 'phone_number', 'email')
    
    actions = ['make_available', 'make_unavailable']

    def make_available(self, request, queryset):
        queryset.update(availability_status=True)
    make_available.short_description = "Mark selected donors as Available"

    def make_unavailable(self, request, queryset):
        queryset.update(availability_status=False)
    make_unavailable.short_description = "Mark selected donors as Unavailable"

admin.site.register(DonorProfile, DonorProfileAdmin)