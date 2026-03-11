from django import forms
from .models import BloodRequest

class BloodRequestForm(forms.ModelForm):

    class Meta:
        model = BloodRequest
        fields = [
            'patient_name',
            'blood_group_needed',
            'units_required',
            'hospital_name',
            'city',
            'latitude',
            'longitude',
            'contact_number',
            'is_emergency'
        ]