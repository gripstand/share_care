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
from users.views import CustomTwoFactorLoginView
from django.contrib.auth import views as auth_views
from two_factor.urls import urlpatterns as tf_urls

urlpatterns = [
    # 1. Include your custom user/auth paths FIRST.
    #    Your users.urls should define all 4 password reset steps and the login view.
    path('users/', include('users.urls')), 

    # 2. Add specific login path (optional, if you want it outside of users.urls)
   
    
    # 3. Remove these conflicting lines:
    # path('',include(tf_urls)), 
    # path("accounts/", include("django.contrib.auth.urls")), 
    # path('',include(tf_urls)), 

    # 4. Keep other paths
    path('account/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('client/', include('client.urls')),
    path('equipment/', include('equipment.urls')),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path('forbidden/', TemplateView.as_view(template_name="forbidden.html"), name="forbidden"),
    path('',include(tf_urls)), 
    path('admin/', admin.site.urls, name="admin"),
]


