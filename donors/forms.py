from django import forms
from .models import DonorProfile


class DonorProfileForm(forms.ModelForm):

    class Meta:
        model = DonorProfile

        fields = [
            'full_name',
            'email',
            'phone_number',
            'date_of_birth',
            'weight',
            'blood_group',
            'city',
            'taluk',
            'town_village',
            'area',
            'latitude',
            'longitude',
            'availability_status'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['phone_number'].required = True
        self.fields['date_of_birth'].required = True
        self.fields['weight'].required = True
        
        # Adding a calendar date-picker widget to date of birth for better experience
        self.fields['date_of_birth'].widget = forms.DateInput(attrs={'type': 'date'})

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            from django.utils.timezone import now
            age = (now().date() - dob).days // 365
            if age < 18:
                raise forms.ValidationError(f"You must be at least 18 years old to register as a donor. (Current age: {age})")
            if age > 60:
                raise forms.ValidationError(f"The maximum age limit for blood donation is 60. (Current age: {age})")
        return dob