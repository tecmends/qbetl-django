from django.contrib.auth.models import User
from django.db import models


class UserConnection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    consumer_key = models.CharField(max_length=100,blank=True)
    consumer_secret = models.CharField(max_length=100, blank=True)
    access_token = models.TextField(null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)
    company_id = models.CharField(max_length=500, blank=True)
