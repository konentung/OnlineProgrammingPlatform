from django.contrib import admin
from .models import (
    Question,
    QuestionHistory,
    StudentAnswer,
    PeerReview,
    TeachingMaterial
)

# 題目管理
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "created_at", "updated_at")
    search_fields = ("title", "creator__username")
    list_filter = ("created_at", "updated_at")

# 題目歷史管理
class QuestionHistoryAdmin(admin.ModelAdmin):
    list_display = ("question", "title", "editor", "edited_at")
    search_fields = ("title", "editor__username")
    list_filter = ("edited_at",)

# 學生作答管理
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ("student", "question", "submitted_at", "updated_at")
    search_fields = ("student__username", "question__title")
    list_filter = ("submitted_at", "updated_at")

# 作答歷史管理
class AnswerHistoryAdmin(admin.ModelAdmin):
    list_display = ("student", "student_answer", "submitted_at")
    search_fields = ("student__username", "student_answer__question__title")
    list_filter = ("submitted_at",)

# 學生互評管理
class PeerReviewAdmin(admin.ModelAdmin):
    list_display = ("reviewer", "reviewed_question", "reviewed_at")
    search_fields = ("reviewer__username", "reviewed_question__question__title")
    list_filter = ("reviewed_at",)
    list_display_links = ("reviewer", "reviewed_question")

# 教材管理
class TeachingMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "updated_at")
    search_fields = ("title",)
    list_filter = ("created_at", "updated_at")

# 題目指派管理
class QuestionAssignmentAdmin(admin.ModelAdmin):
    list_display = ("question", "student", "assigned_at")
    search_fields = ("question__title", "student__username")
    list_filter = ("assigned_at",)

# 註冊模型到 Django Admin
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionHistory, QuestionHistoryAdmin)
admin.site.register(StudentAnswer, StudentAnswerAdmin)
admin.site.register(PeerReview, PeerReviewAdmin)
admin.site.register(TeachingMaterial, TeachingMaterialAdmin)