from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import Student
from posts.models import QuestionData, QuestionAssignment
from posts.forms import QuestionDataForm, QuestionAssignmentForm
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.utils import timezone

@login_required(login_url='Login')
def question_create(request):
    if request.method == 'POST':
        form = QuestionDataForm(request.POST, user=request.user)
        if form.is_valid():
            # 保存 QuestionData 表單並自動設置 student 為當前使用者
            question_data = form.save(commit=False)
            student = Student.objects.get(username=request.user.username)
            question_data.student = student
            question_data.save()

            return redirect('/')
        else:
            print(form.errors)  # 打印錯誤訊息
    else:
        # 初始化表單，並自動設置 student 為當前使用者
        form = QuestionDataForm(user=request.user)
    
    return render(request, 'questions/question_create.html', {'form': form, 'mode': 'edit'})

@login_required(login_url='Login')
def question_detail(request, pk):
    try:
        questions = QuestionData.objects.all()
        questions = get_object_or_404(QuestionData, pk=pk)
    except QuestionData.DoesNotExist:
        raise Http404("No MyModel matches the given query.")
    return render(request, 'questions/PostBase.html', {'question': questions})

@login_required(login_url='Login')
def question_update(request, pk):
    try:
        question = get_object_or_404(QuestionData, pk=pk)
        if request.method == 'POST':
            form = QuestionDataForm(request.POST, instance=question, user=request.user)
            if form.is_valid():
                form.save()
                return redirect('QuestionDetail', pk=question.pk)
            else:
                print(form.errors)
        else:
            form = QuestionDataForm(instance=question, user=request.user)
    except QuestionData.DoesNotExist:
        raise Http404("No MyModel matches the given query.")
    return render(request, 'questions/question_update.html', {'form': form, 'question': question})

@login_required(login_url='Login')
def question_delete(request, pk):
    question = get_object_or_404(QuestionData, pk=pk)
    question.delete()
    return redirect('/')

@login_required(login_url='Login')
def question_assignment(request):
    question_assignments = QuestionAssignment.objects.filter(student=request.user)
    return render(request, 'questions/question_assignment.html', {'question_assignments': question_assignments})

# @login_required(login_url='Login')
# def submit_answer(request, pk):
#     question = get_object_or_404(QuestionData, pk=pk)
#     assignment, created = QuestionAssignment.objects.get_or_create(
#         student=request.user,
#         question_data=question
#     )

#     # 取得 URL 中的 mode 參數，默認為 'view'
#     mode = request.GET.get('mode', 'view')

#     if request.method == 'POST':
#         form = QuestionAssignmentForm(request.POST, instance=assignment)
#         if form.is_valid():
#             form.instance.submitted_at = timezone.now()
#             form.instance.status = 'submitted'
#             form.save()
#             return redirect('QuestionAssignment')
#     else:
#         form = QuestionAssignmentForm(instance=assignment)

#     return render(request, 'questions/PostBase.html', {'question': question, 'form': form, 'mode': mode})

@login_required(login_url='Login')
def submit_answer(request, pk):
    question = get_object_or_404(QuestionData, pk=pk)
    assignment, created = QuestionAssignment.objects.get_or_create(
        student=request.user,
        question_data=question
    )

    mode = request.GET.get('mode', 'view')

    if request.method == 'POST':
        form = QuestionAssignmentForm(request.POST, instance=assignment)
        if form.is_valid() and assignment.status != 'graded':  # 僅當未評分時才允許保存
            form.instance.submitted_at = timezone.now()
            form.instance.status = 'submitted'
            form.save()
            return redirect('QuestionAssignment')
    else:
        form = QuestionAssignmentForm(instance=assignment)

    return render(request, 'questions/PostBase.html', {
        'question': question,
        'form': form,
        'mode': mode,
        'status': assignment.status,  # 傳遞 status 以便在模板中使用
        'score' : assignment.score # 傳遞 score 以便在模板中使用
    })