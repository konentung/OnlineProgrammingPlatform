from django import forms
from .models import QuestionData, QuestionAssignment
from accounts.models import Student

class QuestionDataForm(forms.ModelForm):
    CATEGORY_CHOICES = (
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

    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        label='選擇題目類別',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    display_student = forms.CharField(
        label='使用者名稱',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(QuestionDataForm, self).__init__(*args, **kwargs)
        
        if self.user:
            self.fields['display_student'].initial = self.user.username
            self.fields['student'].initial = Student.objects.get(username=self.user.username)
        
        self.fields['student'].widget = forms.HiddenInput()
        self.fields['student'].required = False
        self.fields['title'].required = True
        self.fields['description'].required = True
        self.fields['score'].required = False
        self.fields['difficulty'].required = False

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('student'):
            cleaned_data['student'] = Student.objects.get(username=self.user.username)
        if not cleaned_data.get('title'):
            raise forms.ValidationError('標題不能為空')
        if not cleaned_data.get('description'):
            raise forms.ValidationError('描述不能為空')
        if not cleaned_data.get('score'):
            cleaned_data['score'] = 0
        if not cleaned_data.get('difficulty'):
            cleaned_data['difficulty'] = 0
        return cleaned_data

    class Meta:
        model = QuestionData
        fields = ['display_student', 'title', 'description', 'score', 'difficulty', 'student', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'score': forms.NumberInput(attrs={'class': 'form-control'}),
            'difficulty': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'display_student': '使用者名稱',
            'title': '標題',
            'category': '題目類別',
            'description': '描述',
            'score': '分數',
            'difficulty': '難度',
            'category': '題目類別'
        }

class QuestionAssignmentForm(forms.ModelForm):
    class Meta:
        model = QuestionAssignment
        fields = ['answer']
        widgets = {
            'answer': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(QuestionAssignmentForm, self).__init__(*args, **kwargs)
        # 檢查實例是否存在，並且狀態為 "已評分"
        if self.instance and self.instance.status == 'graded':
            # 將 answer 欄位設置為只讀
            self.fields['answer'].widget.attrs['readonly'] = True