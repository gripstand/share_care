from django.db import models
from client.models import Client # Import the Client model
from django.utils import timezone

# Create your models here.

class Equipment(models.Model):
    eq_name=models.CharField(max_length=30)
    EQTYPES=(('System','System'), ('Peripheral','Peripheral'), ('Interface','Interface'), ('Software', 'Software'), ('Other','Other'))
    eq_type=models.CharField(max_length=25,choices=EQTYPES,blank=False,default='System')
    eq_value=models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return self.eq_name

class EquipmentStatus(models.Model):
    status_date=models.DateField()
    STATUSTYPES=(
        ('Inv', 'In Inventory'),
        ('Client','With Client'),
        ('Return','Returned from Client'),
        ('Maint', 'Maintenance'),
        ('Sunset', 'Sunset'),
        ('Lost', 'Lost'),
        ('RTO', 'Returned to owner'),
        ('Unknown', 'Unknown'),
    )
    status=models.CharField(max_length=25,choices=STATUSTYPES,blank=False,default='Inv')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='eq_with_clients', blank=True, null=True)
    equipment= models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='status_history')
    
    def __str__(self):
        return "Update for: " + self.status_date
