"""
URL configuration for blood_donor_system project.
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    # Dashboard
    path('', views.home, name='home'),

    # Admin
    path('admin/', admin.site.urls),

    # Apps
    path('donors/', include('donors.urls')),
    path('accounts/', include('accounts.urls')),
    path('requests/', include('requests_app.urls')),

    # Authentication
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='registration/login.html'
        ),
        name='login'
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(
            next_page='login'
        ),
        name='logout'
    ),
    path('requests/', include('requests_app.urls')),
    path('requests/', include('requests_app.urls')),

]