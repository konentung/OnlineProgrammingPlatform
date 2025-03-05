from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import Account

class RegisterForm(UserCreationForm):
    class Meta:
        model = Account
        fields = ['username', 'email', 'c_name','nickname', 'student_id', 'gender', 'phone', 'password1', 'password2']

    username = forms.CharField(
        label="帳號",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    phone = forms.CharField(
        label="手機號碼",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        label="電子郵件",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    c_name = forms.CharField(
        label="中文姓名",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    nickname = forms.CharField(
        label="暱稱",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    student_id = forms.CharField(
        label="學號",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    gender = forms.ChoiceField(
        label="性別",
        choices=[('', '請選擇')] + list(Account.GENDER_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    password1 = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    password2 = forms.CharField(
        label="密碼確認",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

class LoginForm(forms.Form):

    username = forms.CharField(
        label="帳號",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    password = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    remember_me = forms.BooleanField(
        label="記住我",
        required=False, 
        widget=forms.CheckboxInput()
    )