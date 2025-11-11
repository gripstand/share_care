from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class CustomUser(AbstractUser):
    #username=None
    email=models.EmailField(max_length=100, unique=True)
    #username=models.CharField(max_length=100)
    username = models.CharField(max_length=100, null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    access_to_system=models.BooleanField('Access to System', default=True)

    # ACCOUNT_USERNAME_REQUIRED = False

    def __str__(self):
        return self.first_name + ' ' + self.last_name