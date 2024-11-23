from django.db import models
from django.contrib.auth.models import AbstractUser

class Student(AbstractUser):
    name = models.CharField(max_length=50, null=False)
    student_id = models.CharField(max_length=9, null=False)
    GENDER_CHOICES = (
        ('M', '男性'),
        ('F', '女性'),
    )
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)