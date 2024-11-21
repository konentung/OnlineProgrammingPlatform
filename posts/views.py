from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from accounts.models import Student
from .models import Question, StudentAnswer, QuestionAssignment, QuestionHistory, PeerReview
from .forms import QuestionForm, StudentAnswerForm, QuestionHistoryForm, PeerReviewForm, QuestionCommentForm
from django.db.models import Q

@login_required(login_url='Login')
def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST, user=request.user)
        if form.is_valid():
            question = form.save(commit=False)
            question.creator = Student.objects.get(username=request.user.username)
            question.save()
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
        form = QuestionForm(user=request.user)
    return render(request, 'questions/question_create.html', {'form': form, 'mode': 'edit'})

# 顯示題目的頁面
def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    comments = question.comments.all()  # 獲取所有相關評論

    if request.method == 'POST':
        comment_form = QuestionCommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.question = question
            new_comment.commenter = request.user  # 假設當前用戶是 Student 模型的實例
            new_comment.save()
            return redirect('QuestionDetail', pk=question.pk)
    else:
        comment_form = QuestionCommentForm()

    return render(request, 'questions/question_detail.html', {
        'question': question,
        'comments': comments,
        'comment_form': comment_form,
    })

# 更新題目的頁面
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
            return redirect('UserQuestionHistoryList')
        else:
            print(form.errors)
    else:
        form = QuestionForm(instance=question, user=request.user)
    
    return render(request, 'questions/question_update.html', {'form': form, 'question': question})

def question_delete(request, pk):
    question = get_object_or_404(Question, pk=pk)
    question.delete()
    return redirect('UserQuestionHistoryList')

# 學生的作業總攬頁面
def question_assignment_list(request):
    # 篩選出所有分配給當前使用者的 QuestionAssignment 實例
    assignments = QuestionAssignment.objects.filter(student=request.user)
    # 使用這些 assignments 中的 question 欄位來篩選 Question
    questions = Question.objects.filter(assignments__in=assignments).distinct()
    return render(request, 'questions/question_assignment_list.html', {'questions': questions})

# 顯示並處理作答的頁面
def question_answer(request, pk):
    question = get_object_or_404(Question, pk=pk)
    # 獲取或創建學生的作答
    student_answer, created = StudentAnswer.objects.get_or_create(student=request.user, question=question)

    if request.method == 'POST':
        if not created:  # 如果資料已經存在，顯示警告並禁止再次提交
            return JsonResponse({"error": "您已經提交過此題的作答，無法再次提交。"}, status=400)

        form = StudentAnswerForm(request.POST, instance=student_answer)
        if form.is_valid() and student_answer.status != 'graded':  # 僅允許未評分的作答進行修改
            student_answer.submitted_at = timezone.now()
            student_answer.status = 'submitted'
            student_answer.save()
            return JsonResponse({"success": "作答提交成功。"})
    else:
        form = StudentAnswerForm(instance=student_answer)

    return render(request, 'questions/question_answer.html', {
        'question': question,
        'form': form,
        'status': student_answer.status,
        'score': student_answer.score if hasattr(student_answer, 'score') else None,
    })

# 顯示該題目的歷史紀錄
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

# 顯示使用者建立的所有題目
def user_question_history_list(request):
    # 獲取當前使用者建立的所有題目
    user_questions = Question.objects.filter(creator=request.user).prefetch_related('edit_history')
    return render(request, 'questions/user_question_history_list.html', {
        'user_questions': user_questions,
    })

# 顯示所有可評分的問題列表，排除當前使用者創建的問題
def peer_assessment_list(request):
    # 取得當前使用者已評分的問題的 ID 和評分時間
    reviewed_questions = PeerReview.objects.filter(reviewer=request.user)

    # 過濾出其他學生創建的問題
    questions_to_review = Question.objects.filter(~Q(creator=request.user))

    # 構建一個查詢集，添加每個問題的評分狀態和時間
    questions_data = []
    for question in questions_to_review:
        # 檢查該問題是否已評分
        review = reviewed_questions.filter(reviewed_question=question).first()
        questions_data.append({
            'question': question,
            'student': question.creator,
            'is_reviewed': review is not None,
            'reviewed_at': review.reviewed_at if review else None
        })

    return render(request, 'questions/question_peer_assessment_list.html', {'questions_data': questions_data})

def peer_assessment(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    # 確保使用者僅對該問題評分一次
    peer_review, created = PeerReview.objects.get_or_create(
        reviewer=request.user,
        reviewed_question=question
    )

    if request.method == 'POST':
        form = PeerReviewForm(request.POST, instance=peer_review)
        if form.is_valid():
            peer_review = form.save(commit=False)
            peer_review.reviewed_at = timezone.now()
            peer_review.save()
            return redirect('PeerAssessmentList')
    else:
        form = PeerReviewForm(instance=peer_review)
        # 設置 reviewer_name 初始值
        form.fields['reviewer_name'].initial = request.user.username

    return render(request, 'questions/question_peer_assessment.html', {
        'question': question,
        'form': form
    })

def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)