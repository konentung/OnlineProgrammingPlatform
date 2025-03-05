from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from accounts.models import Account
from accounts.forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError

# 首頁
def index(request):
    return render(request, 'index.html')

# 登入
def sign_in(request):
    if request.user.is_authenticated:
        # 非 AJAX 請求直接重定向；AJAX 請求回傳 JSON 包含 redirect URL
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'redirect_url': reverse('Index')})
        return redirect(reverse('Index'))
    
    if request.method == "POST":
        form = LoginForm(request.POST) 
        if form.is_valid():
            username = request.POST.get("username")
            password = request.POST.get("password")
            remember_me = request.POST.get("remember_me")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # 如果使用者不是超級使用者，檢查是否驗證過
                if not user.is_superuser and not user.verified:
                    message = '帳號尚未驗證!'
                    return JsonResponse({'message': message})
                # 登入使用者
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                # 如果是 AJAX 請求，回傳 JSON 包含成功與 redirect URL
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'redirect_url': reverse('Index')})
                else:
                    return redirect(reverse('Index'))
            else:
                # 當 user 為 None 時，回傳錯誤訊息
                message = '使用者名稱或密碼錯誤!'
                return JsonResponse({'message': message})
        else:
            message = '驗證碼錯誤!'
            return JsonResponse({'message': message})
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

# 登出
def log_out(request):
    logout(request)
    return redirect('/')

# 註冊
def register(request):
    if request.user.is_authenticated:
        return redirect(reverse('Index'))

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            if Account.objects.filter(username=form.cleaned_data['username']).exists():
                return JsonResponse({'success': False, 'message': '帳號已存在!'})
            if form.cleaned_data['username'] != form.cleaned_data['student_id']:
                return JsonResponse({'success': False, 'message': '帳號與學號不符!'})
            if Account.objects.filter(student_id=form.cleaned_data['student_id']).exists():
                return JsonResponse({'success': False, 'message': '學號已被註冊!'})
            if Account.objects.filter(email=form.cleaned_data['email']).exists():
                return JsonResponse({'success': False, 'message': 'Email已被註冊!'})
            if form.cleaned_data['gender'] == '':
                return JsonResponse({'success': False, 'message': '請選擇性別!'})
            if form.cleaned_data['phone'] == '':
                return JsonResponse({'success': False, 'message': '請輸入手機號碼!'})
            try:
                form.save()
            except IntegrityError:
                return JsonResponse({'success': False, 'message': '帳號已存在!'})
            # 註冊成功時回傳 success true
            return JsonResponse({'success': True})
        else:
            # 彙整 form 驗證錯誤訊息
            errors = "\n".join([msg for error_list in form.errors.values() for msg in error_list])
            return JsonResponse({'success': False, 'message': errors})
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})