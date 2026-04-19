from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .api_views import health_check

urlpatterns = [
    path('', views.landing, name='landing'),
    path('app/', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/export/', views.export_patients_csv, name='export_patients_csv'),
    # Triggering reload
    path('api/chat/', views.api_chat, name='api_chat'),
    path('api/whatsapp/', views.whatsapp_webhook, name='whatsapp_webhook'),
    path('api/facilities/', views.api_facilities, name='api_facilities'),
    path('api/patients/', views.api_patients, name='api_patients'),
    path('api/patients/add/', views.api_patients_add, name='api_patients_add'),
    path('api/medicines/', views.api_medicines, name='api_medicines'),
    path('api/medicines/<int:medicine_id>/toggle/', views.api_medicine_toggle, name='api_medicine_toggle'),
    path('api/profile/update/', views.api_profile_update, name='api_profile_update'),
    path('api/profile/medicines/', views.api_profile_medicines, name='api_profile_medicines'),
    path('api/health/', health_check, name='health_check'),
    path('api/emergency/sos/', views.api_emergency_sos, name='api_emergency_sos'),
    path('referral/<str:session_id>/', views.api_referral_pdf, name='api_referral_pdf'),
]
