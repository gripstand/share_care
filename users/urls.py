from django.contrib import admin
from django.urls import path, include
from . import views
from .views import AllUsers, CustomTwoFactorLoginView
from users.views import CustomTwoFactorLoginView
from two_factor.urls import urlpatterns as tf_urls

urlpatterns = [
    path('create_user/', views.CreateUser, name='user_form'),
    path('list_users/', AllUsers.as_view(), name='list_users'),
    path('update_user/<int:pk>',views.UpdateUser.as_view(),name='update_user'),
    path('user_profile/<int:pk>',views.UserProfile,name='user_profile'),
    path('account/login/', CustomTwoFactorLoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
]