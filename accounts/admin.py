from django.contrib import admin
from .models import Student

class StudentAdmin(admin.ModelAdmin):
	list_display = ("username", "student_id", "email", "is_staff")
	list_filter = ("gender",)
	search_fields=('id',)
	ordering = ("id",)

admin.site.register(Student, StudentAdmin)