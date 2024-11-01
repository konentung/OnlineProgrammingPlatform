from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from accounts.models import Student
from .models import Question, StudentAnswer, QuestionAssignment, QuestionHistory
from .forms import QuestionForm, StudentAnswerForm, QuestionHistoryForm

@login_required(login_url='Login')
def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST, user=request.user)
        if form.is_valid():
            question = form.save(commit=False)
            question.creator = Student.objects.get(username=request.user.username)
            question.save()
            return redirect('/')
        else:
            print(form.errors)
    else:
        form = QuestionForm(user=request.user)
    return render(request, 'questions/question_create.html', {'form': form, 'mode': 'edit'})

@login_required(login_url='Login')
def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    return render(request, 'questions/question_detail.html', {'question': question})

# @login_required(login_url='Login')
# def question_update(request, pk):
#     question = get_object_or_404(Question, pk=pk)
#     if request.method == 'POST':
#         form = QuestionForm(request.POST, instance=question, user=request.user)
#         if form.is_valid():
#             form.save()
#             return redirect('/')
#         else:
#             print(form.errors)
#     else:
#         form = QuestionForm(instance=question, user=request.user)
#     return render(request, 'questions/question_update.html', {'form': form, 'question': question})

@login_required(login_url='Login')
def question_update(request, pk):
    question = get_object_or_404(Question, pk=pk)

    # 在保存更新之前，將原始資料保存到 QuestionHistory 中
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question, user=request.user)
        if form.is_valid():
            form.save()
            # 保存更新前的題目內容到歷史紀錄
            QuestionHistory.objects.create(
                question=question,
                title=question.title,
                description=question.description,
                answer=question.answer,
                editor=request.user,  # 設置當前編輯者
                edited_at=timezone.now()  # 設置編輯時間
            )
            return redirect('/')
        else:
            print(form.errors)
    else:
        form = QuestionForm(instance=question, user=request.user)
    
    return render(request, 'questions/question_update.html', {'form': form, 'question': question})

@login_required(login_url='Login')
def question_delete(request, pk):
    question = get_object_or_404(Question, pk=pk)
    question.delete()
    return redirect('/')

@login_required(login_url='Login')
def question_assignment_list(request):
    assignments = QuestionAssignment.objects.filter(student=request.user)
    return render(request, 'questions/question_assignment_list.html', {'assignments': assignments})

@login_required(login_url='Login')
def submit_answer(request, pk):
    question = get_object_or_404(Question, pk=pk)
    student_answer, created = StudentAnswer.objects.get_or_create(
        student=request.user,
        question=question
    )

    mode = request.GET.get('mode', 'view')

    # 若為新建立作答，初始化狀態為 "pending"
    if created:
        student_answer.status = 'pending'
        student_answer.save()

    if request.method == 'POST':
        form = StudentAnswerForm(request.POST, instance=student_answer)
        # 僅允許 "pending" 狀態進行提交
        if form.is_valid() and student_answer.status == 'pending':
            form.instance.submitted_at = timezone.now()
            form.instance.status = 'submitted'
            form.save()
            return redirect('question_assignment_list')
    else:
        form = StudentAnswerForm(instance=student_answer)

    return render(request, 'questions/submit_answer.html', {
        'question': question,
        'form': form,
        'mode': mode,
        'status': student_answer.status,
        'score': getattr(student_answer, 'score', None)  # 檢查是否存在 score 屬性
    })

@login_required(login_url='Login')
def question_history_list(request, question_id):
    # 確保該問題存在
    question = get_object_or_404(Question, pk=question_id)
    
    # 在視圖中，先查詢資料庫中的資料
    history_records = QuestionHistory.objects.filter(question=question).order_by('-edited_at')

    # 將查詢的資料傳遞給模板
    return render(request, 'questions/question_history_list.html', {
        'history_records': history_records,
        'form': QuestionHistoryForm()
    })

@login_required(login_url='Login')
def user_question_history_list(request):
    # 獲取當前使用者建立的所有題目
    user_questions = Question.objects.filter(creator=request.user).prefetch_related('edit_history')
    return render(request, 'questions/user_question_history_list.html', {
        'user_questions': user_questions,
    })