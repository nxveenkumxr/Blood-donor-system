from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_donor, name='register_donor'),
    path('list/', views.donor_list, name='donor_list'),
    path('detail/<int:donor_id>/', views.donor_detail, name='donor_detail'),
    path('toggle/<int:donor_id>/', views.toggle_availability, name='toggle_availability'),
    path('record_donation/<int:donor_id>/', views.record_donation, name='record_donation'),
]