from django.db import models

# 角色
class Character(models.Model):
    name = models.CharField(max_length=100)
    identity = models.CharField(max_length=100)
    feature = models.CharField(max_length=300)
    background = models.CharField(max_length=300)
    blood = models.IntegerField()
    
# 關卡
class Level(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    difficulty = models.IntegerField()
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    clear = models.BooleanField(default=False)

# 道具
class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)