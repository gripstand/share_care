from django.db import models
from client.models import Client # Import the Client model
from share_care.select_choices import EQStatusList, EquipmentTypes, EquipmentOwnerList
from django_currentuser.db.models import CurrentUserField
from django.utils import timezone

# Create your models here.

class Equipment(models.Model):
    eq_name=models.CharField(max_length=30, verbose_name='Equipment Name or Slug')
    eq_serial_number=models.CharField(max_length=50, blank=True, null=True, verbose_name="Equipment Serial / ID Number")
    eq_type=models.CharField(max_length=25,choices=EquipmentTypes.choices,blank=False,default='System', verbose_name="Equipment Type")
    eq_value=models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Equipment Value")
    eq_owner=models.CharField(max_length=25,choices=EquipmentOwnerList.choices,blank=False,default='Foundation', verbose_name="Equipment Owner")
    eq_date=models.DateField(default=timezone.now, verbose_name="Equipment Date Acquired")
    eq_client=models.ForeignKey(Client, on_delete=models.CASCADE, related_name='eq_client_owner', blank=True, null=True, verbose_name="Client Owner")
    eq_funding_source=models.ForeignKey('client.FundingSources', on_delete=models.CASCADE, blank=True, null=True, related_name='eq_funding_source', verbose_name="Funding Source")
    eq_active_status=models.BooleanField(default=True, verbose_name="Equipment is active")
    eq_notes=models.TextField(blank=True, null=True, verbose_name="Equipment Notes")
    
    def __str__(self):
        return self.eq_name

class EquipmentStatus(models.Model):
    status_date=models.DateField(default=timezone.now)
    status=models.CharField(max_length=25,choices=EQStatusList.choices,blank=False,default='Inv')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='eq_with_clients', blank=True, null=True)
    status_notes=models.TextField(blank=True, null=True, verbose_name="Update Notes")
    equipment= models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='status_history')
    
    def __str__(self):
        return "Update for: " + self.status_date
