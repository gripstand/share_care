"""
URL configuration for share_care project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.views.generic.base import TemplateView
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from users.views import CustomTwoFactorLoginView
from two_factor.urls import urlpatterns as tf_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('client/', include('client.urls')),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path('users/', include('users.urls')),
    path('equipment/', include('equipment.urls')),
    path('account/login/', CustomTwoFactorLoginView.as_view(), name='login'),
    path('',include(tf_urls)),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
# your_project/urls.py


