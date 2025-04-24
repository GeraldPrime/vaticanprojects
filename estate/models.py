from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    
    date_joined = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(null=True, blank=True)
        
    def __str__(self):
        return self.username
