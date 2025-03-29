from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from .models import Character, Level, Chapter, QuestionType, QuestionRed, QuestionBlue, Line, ChapterFlow, UserChapterRecord, UserLevelRecord, UserLineRecord, UserQuestionRecord

# CharacterAdmin
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'Cname', 'Ename', 'identity', 'feature', 'background')

# LevelAdmin
class LevelAdmin(admin.ModelAdmin):
    list_display = ('level_name', 'description', 'clear')

# ChapterAdmin
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('chapter_id', 'chapter_name', 'description', 'clear')

# QuestionTypeAdmin
class QuestionTypeAdmin(admin.ModelAdmin):
    list_display = ('question_type',)

# QuestionRedAdmin
class QuestionRedAdmin(admin.ModelAdmin):
    list_display = ('question', 'option1', 'option2', 'option3', 'option4', 'answer', 'correct', 'level', 'chapter', 'question_type')

# QuestionBlueAdmin
class QuestionBlueAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'correct', 'level', 'chapter', 'question_type')

# LineAdmin
class LineAdmin(admin.ModelAdmin):
    list_display = ('content', 'speaker', 'listener', 'chapter')

# ChapterFlowAdmin
class ChapterFlowAdmin(admin.ModelAdmin):
    list_display = ('chapter', 'level', 'order', 'line', 'question_red', 'question_blue')

# UserChapterRecordAdmin
class UserChapterRecordAdmin(admin.ModelAdmin):
    list_display = ('account', 'chapter', 'cleared')

# UserLevelRecordAdmin
class UserLevelRecordAdmin(admin.ModelAdmin):
    list_display = ('account', 'level', 'cleared')

# UserLineRecordAdmin
class UserLineRecordAdmin(admin.ModelAdmin):
    list_display = ('account', 'line', 'cleared')

# UserQuestionRecordAdmin
class UserQuestionRecordAdmin(admin.ModelAdmin):
    list_display = ('account', 'answered_count', 'correct_count', 'cleared')

admin.site.register(Character, CharacterAdmin)
admin.site.register(Level, LevelAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(QuestionType, QuestionTypeAdmin)
admin.site.register(QuestionRed, QuestionRedAdmin)
admin.site.register(QuestionBlue, QuestionBlueAdmin)
admin.site.register(Line, LineAdmin)
admin.site.register(ChapterFlow, ChapterFlowAdmin)
admin.site.register(UserChapterRecord, UserChapterRecordAdmin)
admin.site.register(UserLevelRecord, UserLevelRecordAdmin)
admin.site.register(UserLineRecord, UserLineRecordAdmin)
admin.site.register(UserQuestionRecord, UserQuestionRecordAdmin)