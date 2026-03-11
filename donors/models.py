from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils.timezone import now

class DonorProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    blood_group = models.CharField(max_length=5)
    city = models.CharField(max_length=100)
    taluk = models.CharField(max_length=100, blank=True, null=True)
    town_village = models.CharField(max_length=100, blank=True, null=True, verbose_name="Town/Village")
    area = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    phone_number = models.CharField(max_length=15)
    availability_status = models.BooleanField(default=True)
    last_donation_date = models.DateField(blank=True, null=True)

    weight = models.PositiveIntegerField(null=True, blank=True, help_text="Weight in kg")
    date_of_birth = models.DateField(null=True, blank=True)

    def is_eligible(self):
        return self.smart_eligibility_check()[0]

    @property
    def eligibility_reason(self):
        return self.smart_eligibility_check()[1]

    def smart_eligibility_check(self):
        """Smart eligibility check based on multiple health parameters."""
        if self.last_donation_date:
            if now().date() < self.last_donation_date + timedelta(days=90):
                return False, "Has donated within the last 90 days."
                
        if self.weight and self.weight < 50:
            return False, f"Underweight ({self.weight}kg). Minimum is 50kg."
            
        if self.date_of_birth:
            age = (now().date() - self.date_of_birth).days // 365
            if age < 18:
                return False, f"Underage ({age}). Must be at least 18."
            if age > 60:
                return False, f"Over age limit ({age}). Max is 60."

        return True, "Eligible to donate."

    def save(self, *args, **kwargs):
        # Automatically update availability status if ineligible
        if not self.is_eligible():
            self.availability_status = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name