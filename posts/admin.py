from django.contrib import admin
from .models import QuestionData, QuestionCategory, QuestionAssignment

class QuestionsAdmin(admin.ModelAdmin):
    list_display = ("student", "title", "description", "created_time", "updated_time", "score", "difficulty")

class QuestionCategoryAdmin(admin.ModelAdmin):
    list_display = ("question_data", "type")
    
class QuestionAssignmentAdmin(admin.ModelAdmin):
    list_display = ("student", "question_data")

admin.site.register(QuestionData, QuestionsAdmin)
admin.site.register(QuestionAssignment, QuestionAssignmentAdmin)