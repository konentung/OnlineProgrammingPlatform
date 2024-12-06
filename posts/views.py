from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.db.models import Count
from accounts.models import Student
from .models import Question, StudentAnswer, QuestionHistory, PeerReview, TeachingMaterial
from .forms import QuestionForm, StudentAnswerForm, QuestionHistoryForm, PeerReviewForm, QuestionCommentForm, TeachingMaterialForm, FuntionStatus
from django.db.models import Q

# 定義功能狀態
STATUS = FuntionStatus

@login_required(login_url='Login')
def question_create(request):
    status = STATUS.OPEN
    if status == STATUS.FIXING:
        return redirect('Maintenance')
    if status == STATUS.CLOSED:
        return redirect('Close')
    if request.method == 'POST':
        form = QuestionForm(request.POST, user=request.user)
        if form.is_valid():
            question = form.save(commit=False)
            question.creator = Student.objects.get(name=request.user.name)
            question.save()
            # 保存更新前的題目內容到歷史紀錄
            QuestionHistory.objects.create(
                question=question,
                title=question.title,
                description=question.description,
                answer=question.answer,
                input_format=question.input_format,
                output_format=question.output_format,
                input_example=question.input_example,
                output_example=question.output_example,
                hint=question.hint,
                editor=request.user,
                edited_at=timezone.now()
            )
            return redirect('/')
        else:
            print(form.errors)
    else:
        form = QuestionForm(user=request.user)
    return render(request, 'questions/question_create.html', {'form': form, 'mode': 'edit'})

# 顯示題目的頁面
def question_detail(request, pk):
    status = STATUS.OPEN
    if status == STATUS.FIXING:
        return redirect('Maintenance')
    if status == STATUS.CLOSED:
        return redirect('Close')
    question = get_object_or_404(Question, pk=pk)
    comments = question.comments.all()  # 獲取所有相關評論

    if request.method == 'POST':
        comment_form = QuestionCommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.question = question
            new_comment.commenter = request.user
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
    status = STATUS.OPEN
    if status == STATUS.FIXING:
        return redirect('Maintenance')
    if status == STATUS.CLOSED:
        return redirect('Close')
    question = get_object_or_404(Question, pk=pk)

    # 在保存更新之前，將原始資料保存到 QuestionHistory 中
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question, user=request.user)

        if form.is_valid():
            changed_fields = form.changed_data  # 獲取有更動的欄位
            
            # 檢查不允許的欄位是否有被更改
            forbidden_fields = ['title', 'editor', 'difficulty']
            illegal_changes = [field for field in changed_fields if field in forbidden_fields]

            if illegal_changes:
                # 返回一個 JsonResponse 提示使用者不允許更改這些欄位
                return JsonResponse({
                    'status': 'error',
                    'message': f"以下欄位不允許更動: {', '.join(illegal_changes)}"
                })

            # 如果允許更動，則先保存歷史紀錄
            if changed_fields:
                QuestionHistory.objects.create(
                    question=question,
                    title=question.title,
                    description=question.description,
                    answer=question.answer,
                    input_format=question.input_format,
                    output_format=question.output_format,
                    input_example=question.input_example,
                    output_example=question.output_example,
                    hint=question.hint,
                    editor=request.user,  # 設置當前編輯者
                    edited_at=timezone.now()  # 設置編輯時間
                )
                
                # 保存新的數據到題目
                form.save()

            return JsonResponse({'status': 'success', 'message': '題目已成功更新！'})
        else:
            # 如果表單無效，返回表單錯誤
            print(form.errors)
            return JsonResponse({
                'status': 'error',
                'message': '表單無效，請檢查輸入資料。',
                'errors': form.errors
            })
    else:
        form = QuestionForm(instance=question, user=request.user)

    return render(request, 'questions/question_update.html', {'form': form})

# 刪除題目按鈕的處理
def question_delete(request, pk):
    status = STATUS.OPEN
    if status == STATUS.FIXING:
        return redirect('Maintenance')
    if status == STATUS.CLOSED:
        return redirect('Close')
    question = get_object_or_404(Question, pk=pk)
    question.delete()
    return redirect('UserQuestionHistoryList')

# 學生的作業總攬頁面
def question_assignment_list(request):
    status = STATUS.CLOSED
    if status == STATUS.FIXING:
        return redirect('Maintenance')
    if status == STATUS.CLOSED:
        return redirect('Close')
    # 篩選出所有分配給當前使用者的 QuestionAssignment 實例
    # 使用這些 assignments 中的 question 欄位來篩選 Question
    questions = Question.objects.filter(as_homework=True)
    return render(request, 'questions/question_assignment_list.html', {'questions': questions})

# 顯示並處理作答的頁面
def question_answer(request, pk):
    status = STATUS.CLOSED
    if status == STATUS.FIXING:
        return redirect('Maintenance')
    if status == STATUS.CLOSED:
        return redirect('Close')
    question = get_object_or_404(Question, pk=pk)
    # 獲取或創建學生的作答
    student_answer, created = StudentAnswer.objects.get_or_create(student=request.user, question=question)

    if request.method == 'POST':
        # 如果學生已經提交過作答，不允許再次提交
        if not created and student_answer.status == 'submitted':
            return JsonResponse({"error": "您已經提交過此題的作答，無法再次提交。"}, status=400)

        form = StudentAnswerForm(request.POST, instance=student_answer)

        if form.is_valid():
            # 只允許未評分的作答進行提交或修改
            if student_answer.status != 'graded':
                student_answer.submitted_at = timezone.now()
                student_answer.status = 'submitted'
                form.save()
                return JsonResponse({"success": "作答提交成功。"})
            else:
                return JsonResponse({"error": "作答已經評分，無法修改。"})
        else:
            return JsonResponse({"error": "有欄位未填寫或格式錯誤。"})

    # 如果是 GET 請求，展示表單
    form = StudentAnswerForm(instance=student_answer)

    return render(request, 'questions/question_answer.html', {
        'question': question,
        'form': form,
        'status': student_answer.status,
        'score': student_answer.score if hasattr(student_answer, 'score') else None,
    })

# 顯示該題目的歷史紀錄
def question_history_list(request, question_id):
    status = STATUS.OPEN
    if status == STATUS.FIXING:
        return redirect('Maintenance')
    if status == STATUS.CLOSED:
        return redirect('Close')
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
    status = STATUS.OPEN
    if status == STATUS.FIXING:
        return redirect('Maintenance')
    if status == STATUS.CLOSED:
        return redirect('Close')
    # 獲取當前使用者建立的所有題目
    user_questions = Question.objects.filter(creator=request.user).prefetch_related('edit_history')
    return render(request, 'questions/user_question_history_list.html', {
        'user_questions': user_questions,
    })

# 顯示所有可評分的問題列表，排除當前使用者創建的問題
def peer_assessment_list(request):
    status = STATUS.CLOSED
    if status == STATUS.FIXING:
        return redirect('Maintenance')
    if status == STATUS.CLOSED:
        return redirect('Close')
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

# 顯示評分頁面
def peer_assessment(request, question_id):
    status = STATUS.CLOSED
    if status == STATUS.FIXING:
        return redirect('Maintenance')
    if status == STATUS.CLOSED:
        return redirect('Close')
    question = get_object_or_404(Question, pk=question_id)
    
    # 檢查是否已經存在評分
    peer_review = PeerReview.objects.filter(reviewer=request.user, reviewed_question=question).first()

    if request.method == 'POST':
        # 僅在沒有提交評分的情況下才允許提交
        if peer_review and peer_review.reviewed_at:
            return JsonResponse({"error": "您已經評分過此題目，無法再次修改。"})

        if not peer_review:
            peer_review = PeerReview(reviewer=request.user, reviewed_question=question)
        form = PeerReviewForm(request.POST, instance=peer_review)
        if form.is_valid():
            peer_review = form.save(commit=False)
            peer_review.reviewed_at = timezone.now()
            peer_review.save()
            return JsonResponse({"success": "評分提交成功！\n送出後無法修改，請確認內容無誤。"})
        else:
            return JsonResponse({"error": "有欄位未填寫或格式錯誤。"})

    # GET 請求
    form = PeerReviewForm(instance=peer_review)
    form.fields['reviewer_name'].initial = request.user.name

    # 如果已經評分，將表單設置為只讀
    if peer_review and peer_review.reviewed_at:
        for field in form.fields:
            form.fields[field].widget.attrs['disabled'] = True

    return render(request, 'questions/question_peer_assessment.html', {
        'question': question,
        'form': form,
        'is_disabled': peer_review and peer_review.reviewed_at
    })

# 顯示教師公告頁面
def teacher_dashboard(request):
    status = STATUS.OPEN
    if status == STATUS.FIXING:
        return redirect('Maintenance')
    if status == STATUS.CLOSED:
        return redirect('Close')
    teaching_materials = TeachingMaterial.objects.all()
    return render(request, 'questions/teacher_dashboard.html', {'teaching_materials': teaching_materials})

# 學生出題排行榜
def student_ranking(request):
    status = STATUS.OPEN
    if status == STATUS.FIXING:
        return redirect('Maintenance')
    if status == STATUS.CLOSED:
        return redirect('Close')
    
    # 查詢每個學生的出題數量，並按數量降序排序
    students_with_question_count = Student.objects.annotate(
        question_count=Count('created_questions')
    ).order_by('-question_count')
    
    # 獲取當前用戶
    user = request.user

    # 查找當前登入用戶的出題數量
    user_question_count = students_with_question_count.filter(id=user.id).first()

    # 計算用戶的排名
    user_rank = None
    if user_question_count:
        user_rank = list(students_with_question_count).index(user_question_count) + 1

    return render(request, 'questions/ranking.html', {
        'students_with_question_count': students_with_question_count,
        'user_question_count': user_question_count,
        'user_rank': user_rank,
    })

def user_dashboard(request):
    # 檢查功能狀態
    status = STATUS.OPEN
    if status == STATUS.FIXING:
        return redirect('Maintenance')
    if status == STATUS.CLOSED:
        return redirect('Close')

    # 獲取當前用戶
    user = request.user
    
    student = Student.objects.get(name=user.name)
    
    # 查找當前用戶創建的所有問題、作答和評分
    user_questions = Question.objects.filter(creator=student)
    user_answers = StudentAnswer.objects.filter(student=student)
    user_reviews = PeerReview.objects.filter(reviewer=student)
    user_questions_amount = user_questions.count() if user_questions else 0
    user_answers_amount = user_answers.count() if user_answers else 0

    # 計算使用者總分數
    user_score = 0
    for answer in user_answers:
        if answer.question.difficulty == 'hard':
            user_score += 20
        elif answer.question.difficulty == 'medium':
            user_score += 10
        elif answer.question.difficulty == 'easy':
            user_score += 5
        else:
            user_score += 0

    # 渲染模板並傳遞必要的上下文變量
    return render(request, 'user_dashboard.html', {
        'student': student,
        'user_questions_amount': user_questions_amount,
        'user_answers_amount': user_answers_amount,
        'user_questions': user_questions,
        'user_answers': user_answers,
        'user_reviews': user_reviews,
        'user_score': user_score
    })

# 關閉功能頁面
def close_view(request):
    return render(request, 'close.html')

# 維護中畫面
def maintenance_view(request):
    return render(request, 'maintenance.html')

# 錯誤頁面
def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)