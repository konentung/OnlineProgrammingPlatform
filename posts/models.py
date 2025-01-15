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
    creator = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="created_questions")
    description = models.TextField(blank=True, null=False)
    input_format = models.TextField(blank=True, null=False)
    output_format = models.TextField(blank=True, null=False)
    input_example = models.TextField(blank=True, null=False)
    output_example = models.TextField(blank=True, null=False)
    answer = models.TextField(blank=True, null=True)
    hint = models.TextField(blank=True, null=False)
    difficulty = models.CharField(max_length=10, choices=difficulty_choices, default='select')
    as_homework = models.BooleanField(default=False, blank=True, null=False)
    answer_display = models.BooleanField(default=False, blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class QuestionHistory(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="histories")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=False)
    input_format = models.TextField(blank=True, null=False)
    output_format = models.TextField(blank=True, null=False)
    input_example = models.TextField(blank=True, null=False)
    output_example = models.TextField(blank=True, null=False)
    answer = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="created_question_histories")
    difficulty = models.CharField(max_length=10, choices=Question.difficulty_choices, default='select')
    hint = models.TextField(blank=True, null=False)
    as_homework = models.BooleanField(default=False, blank=True, null=False)
    answer_display = models.BooleanField(default=False, blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# 題目標籤表
class QuestionTag(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="tags")
    tag = models.CharField(max_length=20)

    def __str__(self):
        return self.tag

# 學生作答表(教師指派題目給學生，學生作答)
class StudentAnswer(models.Model):
    STATUS_CHOICES = [
        ('pending', '未作答'),
        ('submitted', '已提交'),
        ('graded', '已評分')
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    answer = models.TextField(blank=True, null=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    score = models.IntegerField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

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
    question_advice = models.TextField(blank=True, null=False)
    answer_advice = models.TextField(blank=True, null=False)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer} for '{self.reviewed_question}'"

# 教材表
class TeachingMaterial(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# 題目留言板
class QuestionComment(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="comments")
    commenter = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(blank=True, null=False)
    commented_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.commenter} for '{self.question.title}'"

# 階段表
class Stage(models.Model):
    STAGE_CHOICES = [
        ('create_questions', '出題階段'),
        ('answer_questions', '作答階段'),
        ('peer_review', '互評階段'),
        ('update_questions', '更新題目階段'),
        ('end', '結束'),
        ('all', '全部')
    ]
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='create_questions')

    def __str__(self):
        return

# 功能表
class FunctionStatus(models.Model):
    function = models.CharField(max_length=50, unique=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.function

class GPTQuestion(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="gpt_questions")
    question = models.TextField(blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question