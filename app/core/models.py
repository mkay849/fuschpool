from django.contrib.auth.models import AbstractUser
from django.db import models


class PickPoolUser(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)
