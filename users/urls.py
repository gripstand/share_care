from django.contrib import admin
from django.urls import path
from . import views
from .views import AllUsers

urlpatterns = [
    path('create_user/', views.CreateUser, name='user_form'),
    path('list_users/', AllUsers.as_view(), name='list_users'),
    path('update_user/<int:pk>',views.UpdateUser.as_view(),name='update_user'),
    path('user_profile/<int:pk>',views.UserProfile,name='user_profile'),
]