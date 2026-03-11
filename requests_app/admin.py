from django.contrib import admin
from .models import BloodRequest

class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'blood_group_needed', 'hospital_name', 'city', 'status', 'is_emergency')
    list_filter = ('status', 'blood_group_needed', 'is_emergency')
    search_fields = ('patient_name', 'city', 'hospital_name')

    actions = ['mark_fulfilled', 'mark_cancelled', 'mark_pending']

    def mark_fulfilled(self, request, queryset):
        queryset.update(status='Fulfilled')
    mark_fulfilled.short_description = "Mark selected requests as Fulfilled"

    def mark_cancelled(self, request, queryset):
        queryset.update(status='Cancelled')
    mark_cancelled.short_description = "Mark selected requests as Cancelled"
    
    def mark_pending(self, request, queryset):
        queryset.update(status='Pending')
    mark_pending.short_description = "Mark selected requests as Pending"

admin.site.register(BloodRequest, BloodRequestAdmin)