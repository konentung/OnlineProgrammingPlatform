from django.db import models
from accounts.models import Student

class QuestionData(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=3000)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    score = models.IntegerField()
    difficulty = models.IntegerField()

    def __str__(self):
        return self.title

class QuestionCategory(models.Model):
    TYPE_CHOICES = (
        ('----請選擇類別----', '----請選擇類別----'),
        ('if-else', 'if-else'),
        ('for-loop', 'for-loop'),
        ('while-loop', 'while-loop'),
        ('function', 'function'),
        ('list', 'list'),
        ('dictionary', 'dictionary'),
        ('string', 'string'),
        ('file', 'file'),
        ('exception', 'exception'),
    )

    question_data = models.ForeignKey(QuestionData, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    def __str__(self):
        return f"{self.question_data.title} - {self.type}"

# class QuestionAssignment(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
#     question_data = models.ForeignKey(QuestionData, on_delete=models.CASCADE, null=True, blank=True)

#     def __str__(self):
#         return self.question_data.title if self.question_data else "No Title Assigned"

class QuestionAssignment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    question_data = models.ForeignKey(QuestionData, on_delete=models.CASCADE, null=True, blank=True)
    answer = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', '待提交'),
        ('submitted', '已提交'),
        ('graded', '已評分'),
    ], default='pending')

    def __str__(self):
        return self.question_data.title if self.question_data else "No Title Assigned"