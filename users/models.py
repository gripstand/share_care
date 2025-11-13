from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
# Create your models here.


    
class CustomUserManager(UserManager):
    # This method is used by Django for credential checking (login).
    def get_by_natural_key(self, username):
        """
        Allows case-insensitive lookups during the login process.
        """
        # --- THIS IS THE CRITICAL FIX ---
        return self.get(username__iexact=username) 

    # We also ensure username is lowercased during user creation 
    # (Important for data integrity)
    def create_user(self, username, email=None, password=None, **extra_fields):
        if username:
            username = username.lower()
        return super().create_user(username, email, password, **extra_fields)

    # Update create_superuser for completeness:
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        if username:
            username = username.lower()
        return super().create_superuser(username, email, password, **extra_fields)
    
class CustomUser(AbstractUser):
    objects = CustomUserManager()
    email=models.EmailField(max_length=100, unique=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    access_to_system=models.BooleanField('Access to System', default=True)

    def save(self, *args, **kwargs):
        """
        Automatically convert username to lowercase before saving to the database.
        """
        if self.username:
            self.username = self.username.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name + ' ' + self.last_name