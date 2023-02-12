from django.contrib import admin
from django.urls import path, include
from django_registration.backends.one_step.views import RegistrationView
from django.shortcuts import redirect

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('recapp.urls')),
     path('accounts/register/',
        RegistrationView.as_view(success_url='/app/'),
        name='django_registration_register'),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]