from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import JsonResponse
from .models import Line, QuestionRed, QuestionBlue, Chapter, Level, ChapterFlow, UserChapterRecord, UserLevelRecord, UserLineRecord, UserQuestionRecord
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

@login_required
def about(request):
    return render(request, 'games/about.html')

@login_required
def game(request):
    return render(request, 'games/game.html')

@login_required
def notes(request):
    return render(request, 'games/notes.html')

def note_content(request, unit_name):
    template_name = f'notes/{unit_name}.html'
    try:
        return render(request, template_name)
    except Exception:
        raise Http404("單元不存在")

# 設定章節通關
def set_chapter_cleared(request):
    # 如果章節內的所有對話內容以及紅色及藍色題目都回答完成即可設定為cleared
    user_lines = UserLineRecord.objects.filter(cleared=False, account=request.user)
    user_red_questions = UserQuestionRecord.objects.filter(cleared=False, account=request.user, question_red__isnull=False)
    user_blue_questions = UserQuestionRecord.objects.filter(cleared=False, account=request.user, question_blue__isnull=False)
    all_chapters = Chapter.objects.all()
    for chapter in all_chapters:
        if all([line.cleared for line in user_lines if line.line.chapter == chapter]) and all([red_question.cleared for red_question in user_red_questions if red_question.question_red.chapter == chapter]) and all([blue_question.cleared for blue_question in user_blue_questions if blue_question.question_blue.chapter == chapter]):
            UserChapterRecord.objects.update_or_create(account=request.user, chapter=chapter, defaults={'cleared': True})
        else:
            pass

def set_level_cleared(request):
    user_lines = UserLineRecord.objects.filter(cleared=False, account=request.user)
    user_red_questions = UserQuestionRecord.objects.filter(cleared=False, account=request.user, question_red__isnull=False)
    user_blue_questions = UserQuestionRecord.objects.filter(cleared=False, account=request.user, question_blue__isnull=False)
    all_levels = Level.objects.all()
    for level in all_levels:
        if all([line.cleared for line in user_lines if line.line.level == level]) and all([red_question.cleared for red_question in user_red_questions if red_question.question_red.level == level]) and all([blue_question.cleared for blue_question in user_blue_questions if blue_question.question_blue.level == level]):
            UserLevelRecord.objects.update_or_create(account=request.user, level=level, defaults={'cleared': True})
        else:
            pass

def set_line_cleared(request):
    UserLineRecord.objects.update_or_create(account=request.user, line_id=request.GET.get('line_id'), defaults={'cleared': True})

def set_question_cleared(request):
    question_id = request.GET.get('question_id')
    if not question_id:
        return JsonResponse({'error': 'question_id is required'}, status=400)

    try:
        question_red = QuestionRed.objects.get(id=question_id)
        UserQuestionRecord.objects.update_or_create(account=request.user, question_red=question_red, defaults={'cleared': True})
    except QuestionRed.DoesNotExist:
        try:
            question_blue = QuestionBlue.objects.get(id=question_id)
            UserQuestionRecord.objects.update_or_create(account=request.user, question_blue=question_blue, defaults={'cleared': True})
        except QuestionBlue.DoesNotExist:
            return JsonResponse({'error': 'Invalid question_id'}, status=404)

    return JsonResponse({'message': 'Question cleared successfully.'})

# 取得最小未查看過的對話
def get_min_not_cleared_line(request):
    lines = UserLineRecord.objects.filter(cleared=False, account=request.user)
    if len(lines) == 0:
        # 如果所有對話都已經查看過，將全部的對話改回未查看可以繼續遊戲
        UserLineRecord.objects.filter(account=request.user).update(cleared=False)
        return JsonResponse({'min_line_id': 1})
    else:
        min_line_id = lines[0].line.id
        for line in lines:
            if line.line.id < min_line_id:
                min_line_id = line.line.id
        return JsonResponse({'line_id': min_line_id})

# def get_min_not_cleared_level(request):
#     # 取得使用者目前未通關的 Level 紀錄
#     levels = UserLevelRecord.objects.filter(cleared=False, account=request.user)

#     for level_record in levels:
#         level = level_record.level

#         # 找出該 level 所有紅題與藍題
#         red_questions = QuestionRed.objects.filter(level=level)
#         blue_questions = QuestionBlue.objects.filter(level=level)

#         all_cleared = True

#         # 檢查紅題是否全部 cleared
#         for question in red_questions:
#             try:
#                 record = UserQuestionRecord.objects.get(account=request.user, question_red=question)
#                 if not record.cleared:
#                     all_cleared = False
#                     break
#             except UserQuestionRecord.DoesNotExist:
#                 all_cleared = False
#                 break

#         # 若紅題都 cleared，再檢查藍題
#         if all_cleared:
#             for question in blue_questions:
#                 try:
#                     record = UserQuestionRecord.objects.get(account=request.user, question_blue=question)
#                     if not record.cleared:
#                         all_cleared = False
#                         break
#                 except UserQuestionRecord.DoesNotExist:
#                     all_cleared = False
#                     break

#         if all_cleared:
#             # ✅ 該 level 所有題目已完成，標記通關
#             level_record.cleared = True
#             level_record.save()

#             # # ✅ 將該 level 所有題目紀錄重置為未完成
#             # for question in red_questions:
#             #     UserQuestionRecord.objects.update_or_create(
#             #         account=request.user,
#             #         question_red=question,
#             #         defaults={'cleared': False}
#             #     )
#             # for question in blue_questions:
#             #     UserQuestionRecord.objects.update_or_create(
#             #         account=request.user,
#             #         question_blue=question,
#             #         defaults={'cleared': False}
#             #     )

#     # 再次查詢還有沒有未完成的 Level
#     levels = UserLevelRecord.objects.filter(cleared=False, account=request.user)

#     if levels.count() == 0:
#         # ✅ 全部通關，重置為未完成
#         UserLevelRecord.objects.filter(account=request.user).update(cleared=False)
#         min_level_record = UserLevelRecord.objects.filter(account=request.user, cleared=False).order_by('level_id').first()
#         min_level_name = min_level_record.level.level_name
#         return JsonResponse({'level_name': min_level_name})

#     min_level_record = UserLevelRecord.objects.filter(account=request.user, cleared=False).order_by('level__id').first()
#     min_level_name = min_level_record.level.level_name
#     return JsonResponse({'level_name': min_level_name})

# def get_min_not_cleared_chapter(request):
#     # 先取所有章節記錄（未通關的）
#     # chapters = UserChapterRecord.objects.filter(cleared=False, account=request.user)

#     # for chapter_record in chapters:
#     #     chapter = chapter_record.chapter
#     #     chapter_lines = Line.objects.filter(chapter=chapter)

#     #     all_cleared = True
#     #     for line in chapter_lines:
#     #         try:
#     #             record = UserLineRecord.objects.get(account=request.user, line=line)
#     #             if not record.cleared:
#     #                 all_cleared = False
#     #                 break
#     #         except UserLineRecord.DoesNotExist:
#     #             all_cleared = False
#     #             break

#     #     if all_cleared:
#     #         chapter_record.cleared = True
#     #         chapter_record.save()
            
#             # # ✅ 將該章節內所有 UserLineRecord 設為未讀（cleared=False）
#             # for line in chapter_lines:
#             #     UserLineRecord.objects.update_or_create(
#             #         account=request.user,
#             #         line=line,
#             #         defaults={'cleared': False}
#             #     )

#     # ✅ 重新查一次還有沒有未完成的章節
#     chapters = [
#         record for record in UserChapterRecord.objects.all()
#         if record.account == request.user and not record.cleared
#     ]
#     if len(chapters) == 0:
#         # 全部已通關，重置
#         UserChapterRecord.objects.filter(account=request.user).update(cleared=False)
#         return JsonResponse({'chapter_id': 1})

#     # 否則找最小章節 ID
#     min_chapter_id = min(chapter.chapter.chapter_id for chapter in chapters)
#     return JsonResponse({'chapter_id': min_chapter_id})


# # 取得章節流程
# # 這個函數會回傳指定章節、關卡、對話者、聆聽者的對話流程
# def get_chapter_flow(request):
#     chapter_id = request.GET.get('chapter_id')
#     level_name = request.GET.get('level_name')
#     speaker = request.GET.get('speaker')
#     listener = request.GET.get('listener')

#     if not chapter_id or not level_name or not speaker or not listener:
#         return JsonResponse({'error': 'chapter_id, level_name, speaker and listener are required'}, status=400)

#     try:
#         chapter_obj = Chapter.objects.get(chapter_id=chapter_id)
#         level_obj = Level.objects.get(level_name=level_name)
#     except (Chapter.DoesNotExist, Level.DoesNotExist):
#         return JsonResponse({'error': 'Invalid chapter_id or level_name'}, status=404)

#     flows = ChapterFlow.objects.filter(
#         chapter=chapter_obj,
#         level=level_obj
#     ).order_by('order')
    
#     # 全部撈出來再用 Python 過濾
#     cleared_lines = [
#         record.line.id for record in UserLineRecord.objects.all()
#         if record.account == request.user and record.cleared
#     ]
#     cleared_red = [
#         record.question_red.id for record in UserQuestionRecord.objects.all()
#         if record.account == request.user and record.question_red and record.cleared
#     ]
#     cleared_blue = [
#         record.question_blue.id for record in UserQuestionRecord.objects.all()
#         if record.account == request.user and record.question_blue and record.cleared
#     ]

#     flow_list = []

#     for flow in flows:
#         if flow.line and flow.line.id not in cleared_lines:
#             if flow.line:
#                 spk = flow.line.speaker.name
#                 lst = flow.line.listener.name
#                 if (spk == speaker and lst == listener) or (spk == listener and lst == speaker):
#                     flow_list.append({
#                         "type": "line",
#                         "id": flow.line.id,
#                         "speaker": spk,
#                         "listener": lst,
#                         "content": flow.line.content,
#                     })
#                     UserLineRecord.objects.update_or_create(account=request.user, line=flow.line, defaults={'cleared': True})

#         elif flow.question_red:
#             if flow.question_red.id not in cleared_red and flow.question_red.listener and flow.question_red.listener.name == listener:
#                 # 預設 listener 欄位存在
#                 if flow.question_red.listener and flow.question_red.listener.name == listener:
#                     flow_list.append({
#                         "type": "red_crack",
#                         "id": flow.question_red.id,
#                         "question": flow.question_red.question,
#                         "option1": flow.question_red.option1,
#                         "option2": flow.question_red.option2,
#                         "option3": flow.question_red.option3,
#                         "option4": flow.question_red.option4,
#                         "answer": flow.question_red.answer,
#                         "correct": flow.question_red.correct,
#                     })
#                     UserQuestionRecord.objects.update_or_create(account=request.user, question_red=flow.question_red, defaults={'cleared': True})

#         elif flow.question_blue:
#             if flow.question_blue.id not in cleared_blue and flow.question_blue.listener and flow.question_blue.listener.name == listener:
#                 if flow.question_blue.listener and flow.question_blue.listener.name == listener:
#                     flow_list.append({
#                         "type": "blue_crack",
#                         "id": flow.question_blue.id,
#                         "question": flow.question_blue.question,
#                         "answer": flow.question_blue.answer,
#                         "correct": flow.question_blue.correct,
#                     })
#                     UserQuestionRecord.objects.update_or_create(account=request.user, question_blue=flow.question_blue, defaults={'cleared': True})
#         else:
#             continue
#     if len(flow_list) == 0:
#         flow_list.append({
#             "type": "line",
#             "content": "沒有對話內容。"
#         })

#     return JsonResponse({'flow': flow_list})

# reset to initial state
def reset_game(request):
    UserChapterRecord.objects.filter(account=request.user).update(cleared=False)
    UserLevelRecord.objects.filter(account=request.user).update(cleared=False)
    UserLineRecord.objects.filter(account=request.user).update(cleared=False)
    UserQuestionRecord.objects.filter(account=request.user).update(correct_count=0, answered_count=0, cleared=False)
    return JsonResponse({'message': 'Game reset successfully.'})

@require_POST
@csrf_exempt
def check_answer(request):
    try:
        data = json.loads(request.body)
        question_id = data.get("question_id")
        question_type = data.get("question_type")
        user_answer = data.get("user_answer")
    except (json.JSONDecodeError, KeyError, TypeError):
        return JsonResponse({"error": "Invalid request data"}, status=400)

    if not question_id or not question_type or user_answer is None:
        return JsonResponse({"error": "Missing required fields"}, status=400)

    user = request.user
    is_correct = False

    if question_type == "red_crack":
        try:
            question = QuestionRed.objects.get(id=question_id)
            record = UserQuestionRecord.objects.get(account=user, question_red=question)
        except (QuestionRed.DoesNotExist, UserQuestionRecord.DoesNotExist):
            return JsonResponse({"error": "Red question not found"}, status=404)

        is_correct = (user_answer == question.answer)

    elif question_type == "blue_crack":
        try:
            question = QuestionBlue.objects.get(id=question_id)
            record = UserQuestionRecord.objects.get(account=user, question_blue=question)
        except (QuestionBlue.DoesNotExist, UserQuestionRecord.DoesNotExist):
            return JsonResponse({"error": "Blue question not found"}, status=404)

        is_correct = (user_answer.strip() == question.answer.strip())

    else:
        return JsonResponse({"error": "Invalid question type"}, status=400)

    # 更新答題紀錄
    record.answered_count += 1
    if is_correct:
        record.correct_count += 1
        record.cleared = True
    record.save()

    # 判斷 level 是否全部題目已完成
    level = question.level
    red_questions = QuestionRed.objects.filter(level=level)
    blue_questions = QuestionBlue.objects.filter(level=level)

    all_level_questions_cleared = all(
        UserQuestionRecord.objects.filter(account=user, question_red=q, cleared=True).exists()
        for q in red_questions
    ) and all(
        UserQuestionRecord.objects.filter(account=user, question_blue=q, cleared=True).exists()
        for q in blue_questions
    )

    if all_level_questions_cleared:
        UserLevelRecord.objects.update_or_create(
            account=user,
            level=level,
            defaults={"cleared": True}
        )

        # 確認 chapter 所有 line 和 question 也都完成，才標記 chapter 為 cleared
        chapter = question.chapter
        lines = Line.objects.filter(chapter=chapter)
        red_qs = QuestionRed.objects.filter(chapter=chapter)
        blue_qs = QuestionBlue.objects.filter(chapter=chapter)

        all_lines_cleared = all(
            UserLineRecord.objects.filter(account=user, line=l, cleared=True).exists()
            for l in lines
        )
        all_red_cleared = all(
            UserQuestionRecord.objects.filter(account=user, question_red=q, cleared=True).exists()
            for q in red_qs
        )
        all_blue_cleared = all(
            UserQuestionRecord.objects.filter(account=user, question_blue=q, cleared=True).exists()
            for q in blue_qs
        )

        if all_lines_cleared and (all_red_cleared or all_blue_cleared):
            UserChapterRecord.objects.update_or_create(
                account=user,
                chapter=chapter,
                defaults={"cleared": True}
            )

    return JsonResponse({
        "question_id": question_id,
        "is_correct": is_correct,
        "message": "✅ 答對了！" if is_correct else "❌ 答錯了！"
    })

# ✅ 取得最小尚未通關的關卡（依 Level.id 最小）
def get_min_not_cleared_level(request):
    user = request.user

    for level_record in UserLevelRecord.objects.filter(account=user, cleared=False):
        level = level_record.level

        red_questions = QuestionRed.objects.filter(level=level)
        blue_questions = QuestionBlue.objects.filter(level=level)
        all_red_cleared = all(
            UserQuestionRecord.objects.filter(account=user, question_red=q, cleared=True).exists()
            for q in red_questions
        )
        all_blue_cleared = all(
            UserQuestionRecord.objects.filter(account=user, question_blue=q, cleared=True).exists()
            for q in blue_questions
        )

        if all_red_cleared and all_blue_cleared:
            level_record.cleared = True
            level_record.save()
            # 該關卡完成後，順便將對應章節設為完成
            if hasattr(level, 'chapter'):
                UserChapterRecord.objects.update_or_create(
                    account=user,
                    chapter=level.chapter,
                    defaults={'cleared': True}
                )

    # 查詢尚未完成的關卡
    remaining = UserLevelRecord.objects.filter(account=user, cleared=False).order_by('level__id')
    if remaining.exists():
        return JsonResponse({'level_name': remaining.first().level.level_name if remaining else 'Equality'})

    # 全部完成：重置所有紀錄
    UserLevelRecord.objects.filter(account=user).update(cleared=False)
    UserChapterRecord.objects.filter(account=user).update(cleared=False)
    UserQuestionRecord.objects.filter(account=user).update(cleared=False)
    UserLineRecord.objects.filter(account=user).update(cleared=False)

    # 回傳最小關卡
    first = UserLevelRecord.objects.filter(account=user).order_by('level__id').first()
    return JsonResponse({'level_name': first.level.level_name if first else 'Equality'})

# ✅ 取得最小尚未通關的章節（依 Chapter.chapter_id）
def get_min_not_cleared_chapter(request):
    user = request.user

    for chapter_record in UserChapterRecord.objects.filter(account=user, cleared=False):
        chapter = chapter_record.chapter
        lines = Line.objects.filter(chapter=chapter)
        all_lines_cleared = all(
            UserLineRecord.objects.filter(account=user, line=line, cleared=True).exists()
            for line in lines
        )

        # 如果對話完成，先暫存，等待 level 判斷
        if all_lines_cleared:
            # 先不立即標記 cleared，等 level 那邊一併判斷
            continue

    remaining = UserChapterRecord.objects.filter(account=user, cleared=False).order_by('chapter__chapter_id')
    if remaining.exists():
        return JsonResponse({'chapter_id': remaining.first().chapter.chapter_id if remaining else 1})

    # 全部完成：重置所有紀錄
    UserLevelRecord.objects.filter(account=user).update(cleared=False)
    UserChapterRecord.objects.filter(account=user).update(cleared=False)
    UserQuestionRecord.objects.filter(account=user).update(cleared=False)
    UserLineRecord.objects.filter(account=user).update(cleared=False)

    first = UserChapterRecord.objects.filter(account=user).order_by('chapter__chapter_id').first()
    return JsonResponse({'chapter_id': first.chapter.chapter_id if first else 1})

# 取得章節 + 關卡下的流程，依使用者紀錄過濾
def get_chapter_flow(request):
    chapter_id = request.GET.get('chapter_id')
    level_name = request.GET.get('level_name')
    if chapter_id is None or level_name is None:
        chapter_id = 0
        level_name = 'None'
    speaker = request.GET.get('speaker')
    listener = request.GET.get('listener')

    if not chapter_id or not level_name or not speaker or not listener:
        return JsonResponse({'error': 'no_flow'}, status=200)

    user = request.user
    all_lines_cleared = all(r.cleared for r in UserLineRecord.objects.all() if r.account == user)
    all_red_cleared = all(r.cleared for r in UserQuestionRecord.objects.all() if r.account == user and r.question_red)
    all_blue_cleared = all(r.cleared for r in UserQuestionRecord.objects.all() if r.account == user and r.question_blue)
    all_chapters_cleared = all(r.cleared for r in UserChapterRecord.objects.all() if r.account == user)
    all_levels_cleared = all(r.cleared for r in UserLevelRecord.objects.all() if r.account == user)

    if all([all_lines_cleared, all_red_cleared, all_blue_cleared, all_chapters_cleared, all_levels_cleared]):
        UserLineRecord.objects.filter(account=user).update(cleared=False)
        UserQuestionRecord.objects.filter(account=user).update(cleared=False)
        UserChapterRecord.objects.filter(account=user).update(cleared=False)
        UserLevelRecord.objects.filter(account=user).update(cleared=False)

    try:
        chapter_id = int(chapter_id)
        chapter = Chapter.objects.get(chapter_id=chapter_id)
        level = Level.objects.get(level_name=level_name)
    except (Chapter.DoesNotExist, Level.DoesNotExist):
        return JsonResponse({'error': 'Invalid chapter_id or level_name'}, status=404)

    flows = ChapterFlow.objects.filter(chapter=chapter, level=level).order_by('order')

    # 取使用者紀錄（不用 filter）
    cleared_lines = [r.line.id for r in UserLineRecord.objects.all() if r.account == request.user and r.cleared]
    cleared_red = [r.question_red.id for r in UserQuestionRecord.objects.all() if r.account == request.user and r.question_red and r.cleared]
    cleared_blue = [r.question_blue.id for r in UserQuestionRecord.objects.all() if r.account == request.user and r.question_blue and r.cleared]

    flow_list = []

    for flow in flows:
        if flow.line and flow.line.id not in cleared_lines:
            spk = flow.line.speaker.name
            lst = flow.line.listener.name
            if (spk == speaker and lst == listener) or (spk == listener and lst == speaker):
                flow_list.append({
                    "type": "line",
                    "id": flow.line.id,
                    "speaker": spk,
                    "listener": lst,
                    "content": flow.line.content,
                })
                UserLineRecord.objects.update_or_create(account=request.user, line=flow.line, defaults={'cleared': True})

        elif flow.question_red and flow.question_red.id not in cleared_red:
            if flow.question_red.listener and flow.question_red.listener.name == listener:
                flow_list.append({
                    "type": "red_crack",
                    "id": flow.question_red.id,
                    "question": flow.question_red.question,
                    "option1": flow.question_red.option1,
                    "option2": flow.question_red.option2,
                    "option3": flow.question_red.option3,
                    "option4": flow.question_red.option4,
                    "answer": flow.question_red.answer,
                    "correct": flow.question_red.correct,
                })
                # UserQuestionRecord.objects.update_or_create(account=request.user, question_red=flow.question_red, defaults={'cleared': True})

        elif flow.question_blue and flow.question_blue.id not in cleared_blue:
            if flow.question_blue.listener and flow.question_blue.listener.name == listener:
                flow_list.append({
                    "type": "blue_crack",
                    "id": flow.question_blue.id,
                    "question": flow.question_blue.question,
                    "answer": flow.question_blue.answer,
                    "correct": flow.question_blue.correct,
                })
                # UserQuestionRecord.objects.update_or_create(account=request.user, question_blue=flow.question_blue, defaults={'cleared': True})

    if not flow_list:
        flow_list.append({"type": "line", "content": "沒有對話內容。"})

    return JsonResponse({'flow': flow_list})