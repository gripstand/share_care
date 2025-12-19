from django.urls import path, include
from . import views
from django.contrib import admin
from .views import  ListClients, ClientDetails, UpdateView, ListActions, CreateClient,ClientUpdateView,UpdateGoalView,MyAssignedTicketsListView, CloseTicketView #

urlpatterns=[

    path('',views.index, name='home'),
    path('create_client/', views.CreateClient.as_view(), name='create_client'),
    path('list_clients/', views.ListClients.as_view(), name='list_clients'),
    path('client_detail/<int:pk>/', views.ClientDetails.as_view(), name='client_detail'),
    path('update_client/<int:pk>/', views.ClientUpdateView.as_view(), name='update_client'),
    path('add_goal/<int:client_id>/', views.CreateGoal.as_view(), name='add_goal'),
    path('update_goal/<int:pk>/', UpdateGoalView.as_view(), name='update_goal'),
    path('goal_detail/<int:pk>/', views.GoalDetails.as_view(), name='goal_detail'),
    path('add_goal_update/<int:goal_id>/', views.CreateGoalUpdate.as_view(), name='add_goal_update'),
    path('add_action/<int:client_id>/', views.CreateAction.as_view(), name='add_action'),
    path('action_detail/<int:pk>', views.ActionDetails.as_view(), name='action_detail'),
    path('list_actions/', views.ListActions.as_view(), name='list_actions'),
    path('update_action/<int:pk>', views.UpdateAction.as_view(), name='update_action'),
    path('add_ticket/<int:action_id>', views.CreateTicket.as_view(), name='add_ticket'),
    path('update_ticket/<int:ticket_id>/', views.AddTicketUpdate.as_view(), name='update_ticket'),
    path('list_tickets/', views.ListTickets.as_view(), name='list_tickets'),
    path('tickets/mine/', MyAssignedTicketsListView.as_view(), name='my_tickets_list'),
    path('ticket_detail/<int:pk>/', views.TicketDetails.as_view(), name='ticket_detail'),
    path('tickets/<int:pk>/close/', CloseTicketView.as_view(), name='close_ticket'),
    path('add_eval/<int:client_id>/', views.CreateEval.as_view(), name='add_eval'),
    path('update_eval/<int:pk>/', views.UpdateEval.as_view(), name='update_eval'),
    path('eval_detail/<int:pk>/', views.EvalDetails.as_view(), name='eval_detail'),


]