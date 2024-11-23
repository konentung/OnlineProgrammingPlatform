from django.db import models
from accounts.models import Student

# 題目主表（學生出題，包含解答）
class Question(models.Model):
    difficulty_choices = [
        ('select', '請選擇'),
        ('easy', 'easy'),
        ('medium', 'medium'),
        ('hard', 'hard')
    ]
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=3000)
    input_format = models.TextField(max_length=1000)
    output_format = models.TextField(max_length=1000)
    input_example = models.TextField(max_length=1000)
    output_example = models.TextField(max_length=1000)
    answer = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="created_questions")
    difficulty = models.CharField(max_length=10, choices=difficulty_choices, default='select')
    hint = models.TextField(max_length=500, blank=True, null=True)
    as_homework = models.BooleanField(default=False, blank=True, null=True)
    answer_display = models.BooleanField(default=False, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# 題目歷史表（每次的編輯紀錄）
class QuestionHistory(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="edit_history")
    title = models.CharField(max_length=50)
    difficulty = models.CharField(max_length=10)
    description = models.TextField(max_length=3000)
    input_format = models.TextField(max_length=1000)
    output_format = models.TextField(max_length=1000)
    input_example = models.TextField(max_length=1000)
    output_example = models.TextField(max_length=1000)
    hint = models.TextField(max_length=500, blank=True, null=True)
    answer = models.TextField(max_length=3000)
    editor = models.ForeignKey(Student, on_delete=models.SET_NULL, related_name="edited_questions" ,null=True)
    edited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Edit history of '{self.question.title}' at {self.edited_at}"

# 學生作答表(教師指派題目給學生，學生作答)
class StudentAnswer(models.Model):
    STATUS_CHOICES = [
        ('pending', '未作答'),
        ('submitted', '已提交'),
        ('graded', '已評分')
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    answer = models.TextField(max_length=3000)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Answer by {self.student} for '{self.question.title}'"

# 學生互評表
class PeerReview(models.Model):
    reviewer = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="peer_reviews_given")
    reviewed_question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="peer_reviews_received")
    question_accuracy_score = models.IntegerField(choices=[(i, str(i)) for i in range(6)], default=0)
    complexity_score = models.IntegerField(choices=[(i, str(i)) for i in range(6)], default=0)
    practice_score = models.IntegerField(choices=[(i, str(i)) for i in range(6)], default=0)
    answer_accuracy_score = models.IntegerField(choices=[(i, str(i)) for i in range(6)], default=0)
    readability_score = models.IntegerField(choices=[(i, str(i)) for i in range(6)], default=0)
    comments = models.TextField(max_length=500, blank=True, null=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer} for '{self.reviewed_question}'"

# 教材表
class TeachingMaterial(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=3000, null=True)
    file = models.FileField(upload_to="teaching_materials/", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# 題目評論表
class QuestionComment(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="comments")
    commenter = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(max_length=3000)
    commented_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.commenter} for '{self.question.title}'"