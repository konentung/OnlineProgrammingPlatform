from django.db import models
from accounts.models import Account

# GPT
class GPT(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    user_input = models.TextField()
    ai_output = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Log
class Log(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    chat = models.ForeignKey(GPT, on_delete=models.CASCADE)
    bug_log = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)