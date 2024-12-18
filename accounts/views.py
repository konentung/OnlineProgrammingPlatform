from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from accounts.models import Student
from posts.models import Question
from accounts.forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# 首頁
@login_required(login_url="Login")
def index(request):
    questions = Question.objects.all().order_by('-created_at')
    return render(request, 'index.html', {'questions': questions})

# 登入
def sign_in(request):
    if request.user.is_authenticated:
        return redirect(reverse('Index'))
    
    if request.method == "POST":
        form = LoginForm(request.POST) 
        if form.is_valid():
            username = request.POST.get("username")
            password = request.POST.get("password")
            remember_me = request.POST.get("remember_me")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                return redirect(reverse('Index'))
        else:
            message = '驗證碼錯誤!'
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', locals())

# 登出
def log_out(request):
    logout(request)
    return redirect('/')

# 註冊
def register(request):
    if request.user.is_authenticated:
        return redirect(reverse('Index'))
    
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            return HttpResponse('<script>alert("註冊成功！"); window.location.href = "/login";</script>')
        else:
            message = ''
            for error in form.errors:
                message += (error + "\n")

    return render(request, 'accounts/register.html', locals())

def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)