from django.contrib import admin
from .models import Account

class StudentAdmin(admin.ModelAdmin):
	list_display = ("username", "student_id", "phone", "email", "is_staff", "c_name", "nickname", "bio", "birthday", "gender", "avatar", "verified", "created_at", "updated_at")
	list_filter = ("gender",)
	search_fields=('id',)
	ordering = ("id",)

admin.site.register(Account, StudentAdmin)