from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.html import strip_tags
from django.http import JsonResponse
from django.db.models import Count, Case, When, IntegerField, Sum, F, Window
from accounts.models import Student
from .models import Question, StudentAnswer, QuestionHistory, PeerReview, TeachingMaterial, FunctionStatus, GPTQuestion
from .forms import QuestionForm, StudentAnswerForm, QuestionHistoryForm, PeerReviewForm, QuestionCommentForm, GPTQuestionForm
from django.db.models import Q, Exists, OuterRef
from django.db.models.functions import DenseRank
from openai import OpenAI
import os

def get_function_status(function_name):
    status, created = FunctionStatus.objects.get_or_create(function=function_name, defaults={'status': False})
    return status.status

@login_required(login_url='Login')

# 建立題目的頁面
def question_create(request):
    if get_function_status('question_create'):
        return redirect('Close')
        
    if request.method == 'POST':
        form = QuestionForm(request.POST, user=request.user)
        if form.is_valid():
            if form.cleaned_data.get('difficulty') == 'select':
                return JsonResponse({'success': False, 'errors': {'難度': ['未選擇難度']}}, status=400)
            try:
                creator = Student.objects.get(name=request.user.name)
            except Student.DoesNotExist:
                return JsonResponse({'success': False, 'errors': {'general': ['找不到對應的學生，請確認用戶資料是否完整']}}, status=400)
            
            question = form.save(commit=False)
            question.creator = creator
            question.save()

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
                creator=creator,
                created_at=question.created_at
            )

            return JsonResponse({'success': True, 'message': '題目已成功建立！'}, status=200)
        else:
            # 返回詳細的欄位錯誤訊息
            errors = {}
            for field, error_list in form.errors.items():
                field_label = form.fields[field].label
                errors[field_label] = error_list
            return JsonResponse({'success': False, 'errors': errors}, status=400)

    form = QuestionForm(user=request.user)
    return render(request, 'questions/question_create.html', {'form': form, 'mode': 'edit'})

# 顯示題目的頁面
def question_detail(request, pk):
    if get_function_status('question_detail'):
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
    if get_function_status('question_update'):
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
                    creator=request.user,
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
    if get_function_status('question_delete'):
        return redirect('Close')

    question = get_object_or_404(Question, pk=pk)
    question.delete()
    return redirect('UserQuestionHistoryList')

def question_review(request, question_id):
    if get_function_status('question_review'):
        return redirect('Close')

    # 驗證題目是否存在
    question = get_object_or_404(Question, pk=question_id)

    # 檢索該題目的所有評分
    peer_reviews = PeerReview.objects.filter(reviewed_question=question)

    # 傳遞資料到模板
    return render(request, 'questions/question_review.html', {
        'question': question,
        'peer_reviews': peer_reviews,
    })

# 學生的作業總攬頁面
def question_assignment_list(request):
    if get_function_status('question_assignment_list'):
        return redirect('Close')

    # 篩選出未被學生提交的作答題目
    questions = Question.objects.filter(
        as_homework=True
    ).exclude(
        Exists(
            StudentAnswer.objects.filter(
                student=request.user,
                question=OuterRef('pk'),
                status='submitted'
            )
        )
    )

    return render(request, 'questions/question_assignment_list.html', {'questions': questions})

# 顯示並處理作答的頁面
def question_answer(request, pk):
    if get_function_status('question_answer'):
        return redirect('Close')

    # 獲取題目，但不主動建立 StudentAnswer
    question = get_object_or_404(Question, pk=pk)

    # 嘗試取得現有作答紀錄，但不自動建立
    student_answer = StudentAnswer.objects.filter(student=request.user, question=question).first()

    if request.method == 'POST':
        if not student_answer:
            # 如果還未建立，僅在送出表單時建立
            student_answer = StudentAnswer(student=request.user, question=question)

        # 如果學生已經提交過作答，不允許再次提交
        if student_answer.status == 'submitted':
            return JsonResponse({"error": "您已經提交過此題的作答，無法再次提交。"}, status=400)

        form = StudentAnswerForm(request.POST, instance=student_answer)

        if form.is_valid():
            # 只允許未評分的作答進行提交或修改
            if student_answer.answer == "":
                return JsonResponse({"error": "作答不可為空。"})
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
    form = StudentAnswerForm(instance=student_answer if student_answer else None)

    return render(request, 'questions/question_answer.html', {
        'question': question,
        'form': form,
        'status': student_answer.status if student_answer else 'unattempted',
        'score': student_answer.score if student_answer and hasattr(student_answer, 'score') else None,
    })

# 顯示該題目的歷史紀錄
def question_history_list(request, question_id):
    if get_function_status('question_history_list'):
        return redirect('Close')

    # 確保該問題存在
    question = get_object_or_404(Question, pk=question_id)

    # 在視圖中，先查詢資料庫中的資料
    history_records = QuestionHistory.objects.filter(question=question).order_by('-created_at')

    # 將查詢的資料傳遞給模板
    return render(request, 'questions/question_history_list.html', {
        'history_records': history_records,
        'form': QuestionHistoryForm()
    })

# 顯示使用者建立的所有題目
def user_question_history_list(request):
    if get_function_status('question_history_list'):
        return redirect('Close')

    # 獲取當前使用者建立的所有題目
    user_questions = Question.objects.filter(creator=request.user).prefetch_related('histories')
    return render(request, 'questions/user_question_history_list.html', {
        'user_questions': user_questions,
    })

# 顯示所有可評分的問題列表，排除當前使用者創建的問題
def peer_assessment_list(request):
    if get_function_status('question_peer_assessment_list'):
        return redirect('Close')

    # 確定當前使用者的已評分記錄
    reviewed_questions = PeerReview.objects.filter(reviewer=request.user)

    # 過濾出當前使用者已作答但未創建的問題
    questions_to_review = Question.objects.filter(
        ~Q(creator=request.user),  # 排除自己創建的問題
        Exists(
            StudentAnswer.objects.filter(
                question=OuterRef('pk'),  # 匹配問題的主鍵
                student=request.user     # 僅限當前使用者的回答
            )
        )
    )

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
    if get_function_status('question_peer_assessment'):
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
            # 檢查所有分數欄位是否為 0
            score_fields = ['question_accuracy_score', 'complexity_score', 'practice_score', 'answer_accuracy_score', 'readability_score']
            for field in score_fields:
                if form.cleaned_data.get(field, 0) == 0:
                    # 顯示錯誤訊息
                    error_message = f"{form.fields[field].label} 的分數不可為 0，請重新填寫！"
                    return render(request, 'questions/question_peer_assessment.html', {
                        'question': question,
                        'form': form,
                        'error_message': error_message
                    })

            peer_review = form.save(commit=False)
            peer_review.reviewed_at = timezone.now()
            peer_review.save()
            return JsonResponse({"success": "評分提交成功！\n送出後無法修改，請確認內容無誤。"})
        else:
            return render(request, 'questions/question_peer_assessment.html', {
                'question': question,
                'form': form,
                'error_message': "有欄位未填寫或格式錯誤，請重新檢查！"
            })

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
    if get_function_status('question_teacher_dashboard'):
        return redirect('Close')
    teaching_materials = TeachingMaterial.objects.all()
    return render(request, 'questions/teacher_dashboard.html', {'teaching_materials': teaching_materials})

# 學生排行榜
def student_ranking(request):
    if get_function_status('create_questions'):
        return redirect('Close')

    # 獲取當前用戶
    user = request.user

    # 獲取所有學生的出題數量與排名
    students_with_question_count = (
        Student.objects.annotate(
            question_count=Count('created_questions'),
            rank=Window(
                expression=DenseRank(),
                order_by=F('question_count').desc()
            )
        ).order_by('rank')
    )

    # 獲取當前用戶的出題數量與排名
    user_question_count = None
    for student in students_with_question_count:
        if student.id == user.id:
            user_question_count = {
                'question_count': student.question_count,
                'rank': student.rank
            }
            break

    # 獲取所有學生的總分數與排名
    students_with_scores = (
        Student.objects.annotate(
            total_score=Sum(
                Case(
                    When(answers__question__difficulty='hard', then=20),
                    When(answers__question__difficulty='medium', then=10),
                    When(answers__question__difficulty='easy', then=5),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            rank=Window(
                expression=DenseRank(),
                order_by=F('total_score').desc()
            )
        ).order_by('rank')
    )

    # 獲取當前用戶的總分數與排名
    user_total_score = None
    for student in students_with_scores:
        if student.id == user.id:
            user_total_score = {
                'total_score': student.total_score,
                'rank': student.rank
            }
            break

    return render(request, 'questions/ranking.html', {
        'students_with_question_count': students_with_question_count,
        'students_with_scores': students_with_scores,
        'user_question_count': user_question_count,
        'user_total_score': user_total_score,
    })

def user_dashboard(request):
    if get_function_status('question_user_dashboard'):
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

# 處理GPT API
def ask_gpt(message):
    client = OpenAI(api_key=os.getenv('GPT_API_KEY'))
    # 呼叫 OpenAI API
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": (
                    "你是一個台灣的教學機器人"
                    "不論任何問題，只能回答跟python相關的解答，如果不相關須回答您沒有這方面的知識"
                    "你的專業是引導學生在程式方面的問題，敘述只能用繁體中文，程式碼一律用英文回答"
                )},
                {"role": "user", "content": message}
            ],
            max_tokens=1000,
            temperature=0.2
        )
        ai_reply = completion.choices[0].message.content
    except Exception as e:
        ai_reply = f"發生錯誤：{e}"
    return ai_reply

def chat_view(request):
    chats = GPTQuestion.objects.filter(student=request.user)
    if request.method == 'POST':
        form = GPTQuestionForm(request.POST)
        if form.is_valid():
            user_question = form.cleaned_data.get('question')
            ai_reply = ask_gpt(user_question)

            # 去除 HTML 標籤
            user_question = strip_tags(user_question)
            ai_reply = strip_tags(ai_reply)

            # 儲存對話到資料庫
            new_chat = GPTQuestion(student=request.user, question=user_question, answer=ai_reply, created_at=timezone.now())
            new_chat.save()

            # 更新問答列表
            chats = GPTQuestion.objects.filter(student=request.user)  # 更新問答

            # 使用重定向避免表單重複提交
            return redirect('Chat')
        else:
            print(form.errors)  # 打印表單錯誤
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    return render(request, 'chat.html', {'chats': chats})