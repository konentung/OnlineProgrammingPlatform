from django.db import models
from accounts.models import Student

# 題目主表（學生出題，包含解答）
class Question(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=3000)
    answer = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="created_questions")  # 出題學生
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# 題目歷史表（紀錄每次的編輯歷史）
class QuestionHistory(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="edit_history")
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=3000)
    answer = models.TextField(blank=True, null=True)
    editor = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, related_name="edited_questions")  # 編輯者
    edited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Edit history of '{self.question.title}' at {self.edited_at}"

# 學生作答表，增加狀態欄位
class StudentAnswer(models.Model):
    STATUS_CHOICES = [
        ('pending', '未作答'),
        ('submitted', '已提交'),
        ('graded', '已評分')
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    answer_text = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # 狀態欄位

    def __str__(self):
        return f"Answer by {self.student} for '{self.question.title}'"

# 作答歷史表（包含學生欄位）
class AnswerHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="answer_histories")
    student_answer = models.ForeignKey(StudentAnswer, on_delete=models.CASCADE, related_name="history")
    answer_text = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer history for {self.student} - '{self.student_answer.question.title}'"

# 學生互評表
class PeerReview(models.Model):
    reviewer = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="peer_reviews_given")
    reviewed_answer = models.ForeignKey(StudentAnswer, on_delete=models.CASCADE, related_name="peer_reviews_received")
    question_accuracy_score = models.IntegerField(choices=[(i, str(i)) for i in range(4)], default=0)
    complexity_score = models.IntegerField(choices=[(i, str(i)) for i in range(4)], default=0)
    practice_score = models.IntegerField(choices=[(i, str(i)) for i in range(4)], default=0)
    answer_accuracy_score = models.IntegerField(choices=[(i, str(i)) for i in range(4)], default=0)
    readability_score = models.IntegerField(choices=[(i, str(i)) for i in range(4)], default=0)
    comments = models.TextField(blank=True, null=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer} for '{self.reviewed_answer}'"

# 教材表
class TeachingMaterial(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=3000, blank=True, null=True)
    file = models.FileField(upload_to="teaching_materials/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# 題目指派表（教師指派題目給學生）
class QuestionAssignment(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="assignments")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="assignments")
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Assignment of '{self.question.title}' to {self.student}"

class QuestionComment(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="comments")
    commenter = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(max_length=3000)
    commented_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.commenter} for '{self.question.title}'"