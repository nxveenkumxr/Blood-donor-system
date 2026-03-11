from django.urls import path
from . import views
from .views import create_blood_request
from .views import create_blood_request, request_history, mark_request_completed



urlpatterns = [
    path('create/', views.create_blood_request, name='create_request'),
    path('history/', views.request_history, name='request_history'),
    path('complete/<int:request_id>/', views.mark_request_completed, name='mark_completed'),
    path('approve/<int:request_id>/', views.mark_request_approved, name='mark_approved'),
    path('reject/<int:request_id>/', views.mark_request_rejected, name='mark_rejected'),
    path('find-donors/', views.find_donors, name='find_donors'),
]