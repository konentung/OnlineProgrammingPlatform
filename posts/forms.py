from django import forms
from .models import Question, QuestionHistory, StudentAnswer, PeerReview, TeachingMaterial, QuestionComment
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
            self.fields['display_creator'].initial = self.user.name
            try:
                self.fields['creator'].initial = Student.objects.get(
                    name=self.user.name)
            except Student.DoesNotExist:
                self.fields['creator'].initial = None

        # 隱藏 'creator' 欄位以便由表單內部處理，避免用戶直接編輯
        self.fields['creator'].widget = forms.HiddenInput()
        self.fields['creator'].required = False

        # 設置必填欄位
        self.fields['title'].required = True
        self.fields['description'].required = True
        self.fields['answer'].required = True
        self.fields['input_format'].required = True
        self.fields['output_format'].required = True
        self.fields['input_example'].required = True
        self.fields['output_example'].required = True
        self.fields['hint'].required = True

    def clean(self):
        cleaned_data = super().clean()
        # 確保 'creator' 有值
        if not cleaned_data.get('creator') and self.user:
            try:
                cleaned_data['creator'] = Student.objects.get(
                    name=self.user.name)
            except Student.DoesNotExist:
                raise forms.ValidationError('找不到對應的出題者，請確認用戶存在')

    class Meta:
        model = Question
        fields = ['display_creator', 'title', 'description', 'answer', 'creator', 'input_format', 'output_format', 'input_example', 'output_example', 'difficulty', 'hint']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'answer': forms.Textarea(attrs={'class': 'form-control'}),
            'input_format': forms.Textarea(attrs={'class': 'form-control'}),
            'output_format': forms.Textarea(attrs={'class': 'form-control'}),
            'input_example': forms.Textarea(attrs={'class': 'form-control'}),
            'output_example': forms.Textarea(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
            'hint': forms.Textarea(attrs={'class': 'form-control'}),
        }
        labels = {
            'display_creator': '出題者名稱',
            'title': '標題',
            'description': '描述',
            'answer': '答案',
            'input_format': '輸入格式',
            'output_format': '輸出格式',
            'input_example': '輸入範例',
            'output_example': '輸出範例',
            'difficulty': '難度',
            'hint': '提示',
        }
        required = ['title', 'description', 'answer', 'input_format', 'output_format', 'input_example', 'output_example', 'hint']
        error_messages = {
            'title': {
                'required': '這個欄位需要填寫',
                'max_length': '標題不能超過 100 個字',
            },
            'description': {
                'required': '請提供題目描述',
            },
            'input_format': {
                'required': '請填寫輸入格式',
            },
            'output_format': {
                'required': '請填寫輸出格式',
            },
            'input_example': {
                'required': '請填寫輸入範例',
            },
            'output_example': {
                'required': '請填寫輸出範例',
            },
            'answer': {
                'required': '請填寫答案',
            },
            'hint': {
                'required': '提示不能為空',
            }
        }

# 題目歷史表單（紀錄每次的編輯）
class QuestionHistoryForm(forms.ModelForm):
    class Meta:
        model = QuestionHistory
        fields = [
            'title',
            'difficulty',
            'description',
            'input_format',
            'output_format',
            'input_example',
            'output_example',
            'answer',
            'creator',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'disabled': 'true'}),
            'difficulty': forms.Select(attrs={'class': 'form-control', 'disabled': 'true'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'input_format': forms.Textarea(attrs={'class': 'form-control'}),
            'output_format': forms.Textarea(attrs={'class': 'form-control'}),
            'input_example': forms.Textarea(attrs={'class': 'form-control'}),
            'output_example': forms.Textarea(attrs={'class': 'form-control'}),
            'answer': forms.Textarea(attrs={'class': 'form-control'}),
            'creator': forms.Select(attrs={'class': 'form-control', 'disabled': 'true'}),
        }
        labels = {
            'title': '標題',
            'difficulty': '難度',
            'description': '描述',
            'input_format': '輸入格式',
            'output_format': '輸出格式',
            'input_example': '輸入範例',
            'output_example': '輸出範例',
            'answer': '答案',
            'creator': '編輯者',
        }

# 學生作答表單，根據 status 設定可否編輯
class StudentAnswerForm(forms.ModelForm):
    class Meta:
        model = StudentAnswer
        fields = ['answer']
        widgets = {'answer': forms.Textarea(attrs={'class': 'form-control'})}

    def __init__(self, *args, **kwargs):
        super(StudentAnswerForm, self).__init__(*args, **kwargs)
        # 根據狀態設定是否允許編輯
        if self.instance and self.instance.status in ['submitted', 'graded']:
            self.fields['answer'].widget.attrs['disabled'] = 'disabled'

# 學生互評表單（評分和評論）
class PeerReviewForm(forms.ModelForm):
    reviewer_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'disabled': 'disabled'}),
        required=False,
        label="評分學生"
    )
    SCORE_CHOICES = [(i, str(i)) for i in range(6)]
    question_accuracy_score = forms.ChoiceField(
        choices=SCORE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'style': 'text-align-last: center'}),
        label='題目正確性'
    )
    complexity_score = forms.ChoiceField(
        choices=SCORE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'style': 'text-align-last: center'}),
        label='題目複雜度'
    )
    practice_score = forms.ChoiceField(
        choices=SCORE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'style': 'text-align-last: center'}),
        label='題目實用性'
    )
    answer_accuracy_score = forms.ChoiceField(
        choices=SCORE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'style': 'text-align-last: center'}),
        label='程式正確性'
    )
    readability_score = forms.ChoiceField(
        choices=SCORE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'style': 'text-align-last: center'}),
        label='程式可讀性'
    )
    question_advice = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='題目建議'
    )
    answer_advice = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='程式建議'
    )

    class Meta:
        model = PeerReview
        fields = ['question_accuracy_score', 'complexity_score', 'practice_score', 'answer_accuracy_score', 'readability_score', 'question_advice', 'answer_advice']

# 教材上傳表單
class TeachingMaterialForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TeachingMaterialForm, self).__init__(*args, **kwargs)
        self.fields['file'].required = False

    class Meta:
        model = TeachingMaterial
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': '教材標題',
            'description': '教材描述',
        }

# 留言表單
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