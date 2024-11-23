from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import Student

class RegisterForm(UserCreationForm):
    class Meta:
        model = Student
        fields = ['username', 'email', 'name', 'student_id', 'password1', 'password2']

    username = forms.CharField(
        label="帳號",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        label="電子郵件",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    name = forms.CharField(
        label="姓名",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    student_id = forms.CharField(
        label="學號",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    password1 = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    password2 = forms.CharField(
        label="密碼確認",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

# class RegisterForm(UserCreationForm):
#     username = forms.CharField(
#         label="帳號",
#         widget=forms.TextInput(attrs={'class': 'form-control'})
#     )

#     email = forms.EmailField(
#         label="電子郵件",
#         widget=forms.EmailInput(attrs={'class': 'form-control'})
#     )

#     password1 = forms.CharField(
#         label="密碼",
#         widget=forms.PasswordInput(attrs={'class': 'form-control'})
#     )

#     password2 = forms.CharField(
#         label="密碼確認",
#         widget=forms.PasswordInput(attrs={'class': 'form-control'})
#     )

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