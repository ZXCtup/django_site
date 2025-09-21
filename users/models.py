from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.TextField(verbose_name='Телефон', null=True, blank=True)
