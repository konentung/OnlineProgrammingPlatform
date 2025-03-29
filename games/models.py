from django.db import models
from accounts.models import Account

# 角色
class Character(models.Model):
    name = models.CharField(max_length=100)
    Cname = models.CharField(max_length=100)
    Ename = models.CharField(max_length=100)
    identity = models.CharField(max_length=100)
    feature = models.CharField(max_length=300)
    background = models.CharField(max_length=300)
    
    def __str__(self):
        return self.name
    
# 關卡
class Level(models.Model):
    level_name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    clear = models.BooleanField(default=False)
    
    def __str__(self):
        return self.level_name

# 劇情
class Chapter(models.Model):
    chapter_id = models.IntegerField()
    chapter_name = models.CharField(max_length=100)
    description = models.TextField()
    clear = models.BooleanField(default=False)
    
    def __str__(self):
        return self.chapter_name

# 道具
# class Item(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.CharField(max_length=300)
#     character = models.ForeignKey(Character, on_delete=models.CASCADE)
#     used = models.BooleanField(default=False)

# 台詞
class Line(models.Model):
    line_id = models.IntegerField()
    content = models.CharField(max_length=300)
    speaker = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='speaker')
    listener = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='listener')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.content

class QuestionType(models.Model):
    TYPE_CHOICES = [
        ('red_crack', '紅色裂縫'),
        ('blue_crack', '藍色裂縫')
    ]
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    def __str__(self):
        return self.question_type

# 紅色裂縫選擇題
class QuestionRed(models.Model):
    question = models.TextField()
    option1 = models.TextField()
    option2 = models.TextField()
    option3 = models.TextField()
    option4 = models.TextField()
    OPTION_CHOICES = [
        ('option1', 'option1'),
        ('option2', 'option2'),
        ('option3', 'option3'),
        ('option4', 'option4')
    ]
    answer = models.CharField(max_length=20, choices=OPTION_CHOICES)
    correct = models.BooleanField(default=False)
    level = models.ForeignKey('Level', on_delete=models.CASCADE)
    chapter = models.ForeignKey('Chapter', on_delete=models.CASCADE)
    question_type = models.ForeignKey(QuestionType, on_delete=models.CASCADE)
    listener = models.ForeignKey('Character', on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return self.question

# 藍色裂縫問答題
class QuestionBlue(models.Model):
    question = models.TextField()
    answer = models.TextField()
    correct = models.BooleanField(default=False)
    level = models.ForeignKey('Level', on_delete=models.CASCADE)
    chapter = models.ForeignKey('Chapter', on_delete=models.CASCADE)
    question_type = models.ForeignKey(QuestionType, on_delete=models.CASCADE)
    listener = models.ForeignKey('Character', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.question

class Line(models.Model):
    content = models.CharField(max_length=300)
    speaker = models.ForeignKey('Character', on_delete=models.CASCADE, related_name='speaker')
    listener = models.ForeignKey('Character', on_delete=models.CASCADE, related_name='listener')
    chapter = models.ForeignKey('Chapter', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.content

# 所有對話流程
class ChapterFlow(models.Model):
    """
    這張表用來將「對話」或「題目(紅/藍)」都串接到同一個流程裡。
    只要在同一個 Chapter + Level 下，透過 order 來排序，就能控制
    先出哪幾句對話、再出哪一個題目，以此類推。
    """
    chapter = models.ForeignKey('Chapter', on_delete=models.CASCADE)
    level = models.ForeignKey('Level', on_delete=models.CASCADE, null=True, blank=True)
    
    # 指定此內容在該章節 / 關卡裡的播放 or 出現順序
    order = models.PositiveIntegerField()

    line = models.ForeignKey('Line', on_delete=models.CASCADE, null=True, blank=True)
    question_red = models.ForeignKey('QuestionRed', on_delete=models.CASCADE, null=True, blank=True)
    question_blue = models.ForeignKey('QuestionBlue', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"ChapterFlow (chapter={self.chapter.id}, level={self.level}, order={self.order})"

# 根據使用者記錄他們個別的資料
class UserChapterRecord(models.Model):
    """紀錄使用者是否每個章節通關"""
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    cleared = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.account.username} - {self.chapter.chapter_name}"

class UserLevelRecord(models.Model):
    """紀錄使用者是否每個關卡通關"""
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    cleared = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.account.username} - {self.level.level_name}"

class UserLineRecord(models.Model):
    """紀錄使用者觀看過的對話"""
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    cleared = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.account.username} - {self.line}"

class UserQuestionRecord(models.Model):
    """紀錄使用者答題狀況"""
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    question_red = models.ForeignKey(QuestionRed, on_delete=models.CASCADE, null=True, blank=True)
    question_blue = models.ForeignKey(QuestionBlue, on_delete=models.CASCADE, null=True, blank=True)
    answered_count = models.PositiveIntegerField(default=0)
    correct_count = models.PositiveIntegerField(default=0)
    cleared = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.account.username} - {self.question_red or self.question_blue}"