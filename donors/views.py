from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import DonorProfile
from .forms import DonorProfileForm


@login_required
def register_donor(request):
    donor_profile = DonorProfile.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = DonorProfileForm(request.POST, instance=donor_profile)
        if form.is_valid():
            donor = form.save(commit=False)
            donor.user = request.user
            donor.save()
            return redirect('donor_list')
    else:
        form = DonorProfileForm(instance=donor_profile)

    return render(request, 'donors/register_donor.html', {'form': form})


def donor_list(request):
    donors = DonorProfile.objects.all()

    blood_group = request.GET.get('blood_group')
    city = request.GET.get('city')
    availability = request.GET.get('availability')

    if blood_group:
        donors = donors.filter(blood_group=blood_group)

    if city:
        donors = donors.filter(city__icontains=city)

    if availability == 'True':
        donors = donors.filter(availability_status=True)
    elif availability == 'False':
        donors = donors.filter(availability_status=False)

    context = {
        'donors': donors,
        'selected_blood': blood_group,
        'selected_city': city,
        'selected_availability': availability,
    }

    return render(request, 'donors/donor_list.html', context)


def donor_detail(request, donor_id):
    donor = get_object_or_404(DonorProfile, id=donor_id)
    return render(request, 'donors/donor_detail.html', {'donor': donor})


from django.shortcuts import redirect, get_object_or_404
from .models import DonorProfile

def toggle_availability(request, donor_id):

    donor = get_object_or_404(DonorProfile, id=donor_id)

    donor.availability_status = not donor.availability_status

    donor.save()

    return redirect('donor_list')

from django.utils.timezone import now

def record_donation(request, donor_id):
    donor = get_object_or_404(DonorProfile, id=donor_id)
    donor.last_donation_date = now().date()
    donor.save()
    return redirect('donor_detail', donor_id=donor.id)