from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Case, When, Value, IntegerField
from .models import BloodRequest
from .forms import BloodRequestForm
from donors.models import DonorProfile
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return None
    R = 6371.0 # Radius of earth in km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# -------------------------------
# Create Blood Request + Match Donors
# -------------------------------

def create_blood_request(request):

    matched_donors = None
    alert_message = None
    notification_logs = []

    if request.method == "POST":

        form = BloodRequestForm(request.POST)

        if form.is_valid():

            blood_request = form.save()

            # AI Style Filtering: Location based Distance match first, then city match
            donors_qs = DonorProfile.objects.filter(
                blood_group=blood_request.blood_group_needed,
                availability_status=True
            )
            
            matched_donors = list(donors_qs)
            
            for donor in matched_donors:
                donor.distance = calculate_distance(
                    blood_request.latitude, blood_request.longitude,
                    donor.latitude, donor.longitude
                )
            
            def sort_key(d):
                if d.distance is not None:
                    return (0, d.distance)
                if blood_request.city and d.city.lower() == blood_request.city.lower():
                    return (1, 0)
                if blood_request.city and blood_request.city.lower() in d.city.lower():
                    return (2, 0)
                return (3, 0)
                
            matched_donors.sort(key=sort_key)

            # Emergency alert message & Automatic Notification Simulation
            if matched_donors:
                alert_message = f"🚨 AI Match: {len(matched_donors)} nearby donors found! Automatic SMS/Email notifications sent."
                
                # Send email notification
                from django.core.mail import send_mail
                recipient_list = [donor.email for donor in matched_donors if donor.email]
                if recipient_list:
                    subject = f"Urgent Blood Request: {blood_request.blood_group_needed} needed in {blood_request.city}"
                    message = f"Dear Donor,\n\nAn urgent blood request has been made near your location.\n\nPatient: {blood_request.patient_name}\nBlood Group: {blood_request.blood_group_needed}\nHospital: {blood_request.hospital_name}, {blood_request.city}\nContact: {blood_request.contact_number}\n\nPlease respond if you are available to donate.\n\nThank you,\nBlood Donor System"
                    send_mail(subject, message, 'noreply@blooddonorsystem.local', recipient_list, fail_silently=True)
                    for email in recipient_list:
                        notification_logs.append(f"📧 Email sent to: {email}")

                # Send SMS/WhatsApp notification via Twilio
                try:
                    from twilio.rest import Client
                    import os
                    
                    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', 'AC_dummy_sid')
                    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', 'dummy_token')
                    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '+1234567890')
                    
                    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                    
                    for donor in matched_donors:
                        if donor.phone_number:
                            sms_body = f"URGENT: {blood_request.blood_group_needed} blood needed at {blood_request.hospital_name}, {blood_request.city}. Patient: {blood_request.patient_name}. Contact: {blood_request.contact_number}."
                            
                            # Log to terminal as simulation
                            print(f"[Twilio SMS SIMULATION] To: {donor.phone_number} | Message: {sms_body}")
                            notification_logs.append(f"📱 SMS sent to: {donor.phone_number}")
                            
                            # Uncomment below to enable real Twilio SMS (Make sure TWILIO credentials are valid)
                            # client.messages.create(body=sms_body, from_=TWILIO_PHONE_NUMBER, to=donor.phone_number)
                            
                            # Uncomment below to enable WhatsApp
                            # client.messages.create(body=sms_body, from_=f"whatsapp:{TWILIO_PHONE_NUMBER}", to=f"whatsapp:{donor.phone_number}")

                except Exception as e:
                    print(f"SMS Error: {e}")
                    notification_logs.append("ℹ️ SMS simulation mode enabled (Twilio not configured)")

            else:
                alert_message = "No donors available for this request at the moment."

    else:
        form = BloodRequestForm()

    return render(request, "requests_app/request_form.html", {
        "form": form,
        "matched_donors": matched_donors,
        "alert_message": alert_message,
        "notification_logs": notification_logs
    })
# -------------------------------
# Request History Page
# -------------------------------
def request_history(request):

    requests = BloodRequest.objects.all().order_by('-id')

    return render(request, "requests_app/request_history.html", {
        "requests": requests
    })


# -------------------------------
# Mark Request Status
# -------------------------------
def mark_request_status(request, request_id, new_status):
    blood_request = get_object_or_404(BloodRequest, id=request_id)
    if new_status in dict(BloodRequest.STATUS_CHOICES).keys():
        blood_request.status = new_status
        blood_request.save()
    return redirect('request_history')

def mark_request_completed(request, request_id):
    return mark_request_status(request, request_id, "Completed")

def mark_request_approved(request, request_id):
    return mark_request_status(request, request_id, "Approved")

def mark_request_rejected(request, request_id):
    return mark_request_status(request, request_id, "Rejected")


# -------------------------------
# AJAX Live Donor Finder
# -------------------------------
def find_donors(request):

    blood_group = request.GET.get('blood_group')
    city = request.GET.get('city')

    # AI Style Filtering for Nearby Search
    donors = DonorProfile.objects.filter(
        blood_group__iexact=blood_group,
        availability_status=True
    ).annotate(
        relevance=Case(
            When(city__iexact=city, then=Value(1)),
            When(city__icontains=city, then=Value(2)),
            default=Value(3),
            output_field=IntegerField(),
        )
    ).order_by('relevance', '-id')

    data = []

    for donor in donors:
        data.append({
            "name": "Anonymous Donor",
            "blood_group": donor.blood_group,
            "city": donor.city,
            "phone": "Hidden"
        })

    return JsonResponse({"donors": data})