from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime

class Account(AbstractUser):
    email = models.EmailField()
    phone = models.CharField(max_length=10, blank=True, null=True) # 手機號碼
    student_id = models.CharField(max_length=9, blank=True, null=True) # 學號
    c_name = models.CharField(max_length=30, default='', blank=True, null=True) # 姓名
    nickname = models.CharField(max_length=100, blank=True, null=True) # 暱稱
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
        ('O', '其他'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True) # 性別
    birthday = models.DateField(default=datetime.date(2000, 1, 1), blank=True, null=True) # 生日
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True) # 頭像
    bio = models.TextField(blank=True, null=True) # 自我介紹
    verified = models.BooleanField(default=False) # 是否已驗證
    created_at = models.DateTimeField(auto_now_add=True) # 建立時間
    updated_at = models.DateTimeField(auto_now=True) # 更新時間
    