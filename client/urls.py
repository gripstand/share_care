from django.urls import path, include
from . import views
from django.contrib import admin
from .views import  ListClients, ClientDetails, UpdateView #

urlpatterns=[

    path('',views.index, name='home'),
    path('create_client/', views.create_client, name='create_client'),
    path('list_clients/', views.ListClients.as_view(), name='list_clients'),
    path('client_detail/<int:pk>/', views.ClientDetails.as_view(), name='client_detail'),
    path('update_client/<int:client_id>/', views.update_client, name='update_client'),
    path('add_goal/<int:client_id>/', views.CreateGoal.as_view(), name='add_goal'),
    path('add_goal_update/<int:goal_id>/', views.CreateGoalUpdate.as_view(), name='add_goal_update'),


]