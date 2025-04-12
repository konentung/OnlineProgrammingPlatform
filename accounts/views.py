from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from accounts.models import Account
from accounts.forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from games.models import UserChapterRecord, UserLevelRecord, UserLineRecord, UserQuestionRecord, Chapter, Level, Line, Hint, QuestionRed, QuestionBlue

# 首頁
def index(request):
    cards = [
        ('第零單元：Python 基礎', '涵蓋變數、資料型別、輸入輸出、註解等 Python 初學內容。', 'https://hackmd.io/@KeLeChiang/r113-HhKJg'),
        ('第一單元：「相等性」', '介紹 Python 中的相等運算子（==、!=、is）及其用法差異。', 'https://hackmd.io/@KeLeChiang/SJptkSnKJe'),
        ('第二單元：「運算子與運算」', '介紹 Python 中的基本運算子與運算優先順序。', 'https://hackmd.io/@KeLeChiang/HyXdw-99ke'),
        ('第三單元：「迴圈」', '教學 for loop、while loop 的語法與應用範例。', 'https://hackmd.io/@KeLeChiang/BkTyLi5cyg'),
        ('第四單元：「邏輯控制」', '介紹 if、elif、else 條件語句，與邏輯運算子的運用。', 'https://hackmd.io/@KeLeChiang/ryZw8s99ye'),
        ('第五單元：「函式 Function」', '學會定義與使用函式，掌握參數、回傳值與錯誤除錯技巧。', 'https://hackmd.io/@KeLeChiang/r1YTeKUpkl')
    ]
    return render(request, 'index.html', {'cards': cards})

# 登入
def sign_in(request):
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('Index')
    if request.user.is_authenticated:
        # 非 AJAX 請求直接重定向；AJAX 請求回傳 JSON 包含 redirect URL
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'redirect_url': next_url})
        return redirect(next_url)  # 這裡使用 next_url 而不是 reverse('Index')
    
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
                    return JsonResponse({'success': True, 'redirect_url': next_url})
                else:
                    return redirect(next_url)  # 這裡改成使用 next_url
            else:
                # 當 user 為 None 時，回傳錯誤訊息
                message = '使用者名稱或密碼錯誤!'
                return JsonResponse({'message': message})
        else:
            message = '驗證碼錯誤!'
            return JsonResponse({'message': message})
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})

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
            
            # 建立空的使用者紀錄
            user = Account.objects.get(username=form.cleaned_data['username'])
            chapters = Chapter.objects.all()
            levels = Level.objects.all()
            lines = Line.objects.all()
            hints = Hint.objects.all()
            for hint in hints:
                UserChapterRecord.objects.create(account=user, hint=hint)
            for chapter in chapters:
                UserChapterRecord.objects.create(account=user, chapter=chapter)
            for level in levels:
                UserLevelRecord.objects.create(account=user, level=level)
            for line in lines:
                UserLineRecord.objects.create(account=user, line=line)
            questions_red = QuestionRed.objects.all()
            questions_blue = QuestionBlue.objects.all()
            for question_red in questions_red:
                UserQuestionRecord.objects.create(account=user, question_red=question_red)
            for question_blue in questions_blue:
                UserQuestionRecord.objects.create(account=user, question_blue=question_blue)
            
            # 註冊成功時回傳 success true
            return JsonResponse({'success': True})
        else:
            # 彙整 form 驗證錯誤訊息
            errors = "\n".join([msg for error_list in form.errors.values() for msg in error_list])
            return JsonResponse({'success': False, 'message': errors})
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})