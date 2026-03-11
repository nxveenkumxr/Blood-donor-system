from django.shortcuts import render
from donors.models import DonorProfile
from requests_app.models import BloodRequest
from django.db.models import Count


def home(request):

    total_donors = DonorProfile.objects.count()

    available_donors = DonorProfile.objects.filter(
        availability_status=True
    ).count()

    total_requests = BloodRequest.objects.count()

    recent_requests = BloodRequest.objects.order_by('-id')[:5]

    # Blood group chart
    blood_data = DonorProfile.objects.values('blood_group').annotate(
        count=Count('blood_group')
    )

    blood_groups_list = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    blood_dict = {bg: 0 for bg in blood_groups_list}

    for item in blood_data:
        bg = item['blood_group']
        if bg in blood_dict:
            blood_dict[bg] = item['count']
        else:
            blood_dict[bg] = item['count']

    blood_labels = list(blood_dict.keys())
    blood_counts = list(blood_dict.values())

    # City chart / Top Cities
    city_data = DonorProfile.objects.values('city').annotate(
        count=Count('city')
    ).order_by('-count')

    city_labels = []
    city_counts = []

    for city in city_data:
        if city['city']:
            city_labels.append(city['city'])
            city_counts.append(city['count'])

    if not city_labels:
        city_labels = ['Unknown']
        city_counts = [0]

    # Demand vs Supply Graph
    demand_data = BloodRequest.objects.values('blood_group_needed').annotate(count=Count('id'))
    supply_dict = dict(zip(blood_labels, blood_counts)) # existing all donors
    demand_dict = {bg: 0 for bg in blood_groups_list}
    
    for item in demand_data:
        bg = item['blood_group_needed']
        if bg in demand_dict:
            demand_dict[bg] = item['count']

    demand_counts = list(demand_dict.values())

    # Monthly Trends (last 6 months approximation using TruncMonth)
    from django.db.models.functions import TruncMonth
    monthly_data = BloodRequest.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Count('id')).order_by('month')
    monthly_data_list = list(monthly_data)
    trend_labels = [m['month'].strftime('%b %Y') if m['month'] else 'Unknown' for m in monthly_data_list[-6:]]
    trend_counts = [m['total'] for m in monthly_data_list[-6:]]

    if not trend_labels:
        trend_labels = ['No Data']
        trend_counts = [0]

    top_cities = city_data[:5]

    # Additional Analytics: Request Status Distribution
    status_data = BloodRequest.objects.values('status').annotate(count=Count('id'))
    status_labels = [s['status'] for s in status_data]
    status_counts = [s['count'] for s in status_data]

    # Additional Analytics: Availability Distribution
    availability_data = DonorProfile.objects.values('availability_status').annotate(count=Count('id'))
    availability_labels = ['Available' if a['availability_status'] else 'Not Available' for a in availability_data]
    availability_counts = [a['count'] for a in availability_data]

    return render(request, "dashboard.html", {
        "total_donors": total_donors,
        "available_donors": available_donors,
        "total_requests": total_requests,
        "recent_requests": recent_requests,
        "city_labels": city_labels,
        "city_counts": city_counts,
        "blood_labels": blood_labels,
        "blood_counts": blood_counts,
        "demand_counts": demand_counts,
        "trend_labels": trend_labels,
        "trend_counts": trend_counts,
        "top_cities": top_cities,
        "status_labels": status_labels,
        "status_counts": status_counts,
        "availability_labels": availability_labels,
        "availability_counts": availability_counts,
    })