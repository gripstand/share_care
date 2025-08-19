from django.urls import path
from . import views
from .views import CreateEquipment, ListEquipment,UpdateEquipment,DetailEquipment,CreateEqStatus

urlpatterns = [
    path('add_equipment/', views.CreateEquipment.as_view(), name='add_equipment'),
    path('list_equipment/', views.ListEquipment.as_view(), name='list_equipment'),
    path('update_equipment/<int:pk>/', views.UpdateEquipment.as_view(), name='update_equipment'),
    path('detail_equipment/<int:pk>/', views.DetailEquipment.as_view(), name='detail_equipment'),
    path('create_eq_status/<int:eq_id>/', views.CreateEqStatus.as_view(), name='create_eq_status'),
]