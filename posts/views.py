from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import Student
from posts.models import QuestionAssignment
from posts.forms import QuestionDataForm, QuestionData
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404

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

            # 創建 QuestionAssignment 並將 title 設置為 QuestionData 的 title
            question_assignment = QuestionAssignment.objects.create(
                student=student,
                question_data=question_data
            )
            question_assignment.save()

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
def question_asign(request, pk):
    question = get_object_or_404(QuestionData, pk=pk)
    question.student = Student.objects.get(username=request.user.username)
    question.save()
    return redirect('QuestionDetail', pk=pk)