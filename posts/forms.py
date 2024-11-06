from django import forms
from .models import Question, QuestionHistory, StudentAnswer, AnswerHistory, PeerReview, TeachingMaterial, QuestionAssignment, QuestionComment
from accounts.models import Student

# 題目表單（學生出題）
class QuestionForm(forms.ModelForm):
    display_creator = forms.CharField(
        label='出題者名稱',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(QuestionForm, self).__init__(*args, **kwargs)
        
        if self.user:
            self.fields['display_creator'].initial = self.user.username
            self.fields['creator'].initial = Student.objects.get(username=self.user.username)
        
        self.fields['creator'].widget = forms.HiddenInput()
        self.fields['creator'].required = False
        self.fields['title'].required = True
        self.fields['description'].required = True
        self.fields['answer'].required = True

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('creator'):
            cleaned_data['creator'] = Student.objects.get(username=self.user.username)
        if not cleaned_data.get('title'):
            raise forms.ValidationError('標題不能為空')
        if not cleaned_data.get('description'):
            raise forms.ValidationError('題目敘述不能為空')
        if not cleaned_data.get('answer'):
            raise forms.ValidationError('答案不能為空')

    class Meta:
        model = Question
        fields = ['display_creator', 'title', 'description', 'answer', 'creator']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'answer': forms.Textarea(attrs={'class': 'form-control'}),
        }
        labels = {
            'display_creator': '出題者名稱',
            'title': '標題',
            'description': '描述',
            'answer': '答案',
        }

# 題目歷史表單（紀錄每次的編輯）
class QuestionHistoryForm(forms.ModelForm):
    class Meta:
        model = QuestionHistory
        fields = ['title', 'description', 'answer', 'editor']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }
        labels = {
            'title': '標題',
            'description': '描述',
            'answer': '答案',
        }

# 學生作答表單，根據 status 設定可否編輯
class StudentAnswerForm(forms.ModelForm):
    class Meta:
        model = StudentAnswer
        fields = ['answer_text']
        widgets = {
            'answer_text': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(StudentAnswerForm, self).__init__(*args, **kwargs)
        # 根據狀態設定是否允許編輯
        if self.instance and self.instance.status in ['submitted', 'graded']:
            self.fields['answer_text'].widget.attrs['readonly'] = 'readonly'

# 作答歷史表單（每次作答的紀錄）
class AnswerHistoryForm(forms.ModelForm):
    class Meta:
        model = AnswerHistory
        fields = ['student', 'student_answer', 'answer_text']
        widgets = {
            'answer_text': forms.Textarea(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }
        labels = {
            'student': '學生',
            'student_answer': '作答',
            'answer_text': '作答內容',
        }

# 學生互評表單（評分和評論）
class PeerReviewForm(forms.ModelForm):
    reviewer_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}),
        required=False,
        label="評分學生"
    )
    SCORE_CHOICES = [(i, str(i)) for i in range(6)]
    question_accuracy_score = forms.ChoiceField(choices=SCORE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}), label='題目正確性')
    complexity_score = forms.ChoiceField(choices=SCORE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}), label='題目複雜度')
    practice_score = forms.ChoiceField(choices=SCORE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}), label='題目實用性')
    answer_accuracy_score = forms.ChoiceField(choices=SCORE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}), label='程式正確性')
    readability_score = forms.ChoiceField(choices=SCORE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}), label='程式可讀性')
    comments = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False, label='評論')

    class Meta:
        model = PeerReview
        fields = ['question_accuracy_score', 'complexity_score', 'practice_score', 'answer_accuracy_score', 'readability_score', 'comments']

# 教材上傳表單
class TeachingMaterialForm(forms.ModelForm):
    class Meta:
        model = TeachingMaterial
        fields = ['title', 'description', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': '教材標題',
            'description': '教材描述',
            'file': '檔案',
        }

# 題目指派表單
class QuestionAssignmentForm(forms.ModelForm):
    class Meta:
        model = QuestionAssignment
        fields = ['question', 'student']
        widgets = {
            'question': forms.Select(attrs={'class': 'form-control'}),
            'student': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'question': '題目',
            'student': '學生',
        }

class QuestionCommentForm(forms.ModelForm):
    class Meta:
        model = QuestionComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '輸入您的評論...', 'rows': 3}),
        }
        labels = {
            'content': '新增評論',
        }