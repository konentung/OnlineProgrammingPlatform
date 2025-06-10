from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import JsonResponse
from .models import Character, Line, Hint, QuestionRed, QuestionBlue, QuestionBig, Chapter, Level, ChapterFlow, UserChapterRecord, UserLevelRecord, UserLineRecord, UserQuestionRecord, UserHintRecord
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

def about(request):
    return render(request, 'games/about.html')

@login_required
def game(request):
    return render(request, 'games/game.html')

# reset to initial state
def reset_game(request):
    UserChapterRecord.objects.filter(account=request.user).update(cleared=False)
    UserLevelRecord.objects.filter(account=request.user).update(cleared=False)
    UserLineRecord.objects.filter(account=request.user).update(cleared=False)
    UserQuestionRecord.objects.filter(account=request.user).update(cleared=False)
    UserHintRecord.objects.filter(account=request.user).update(cleared=False)
    return JsonResponse({'message': 'Game reset successfully.'})

def reset_user_all_game_data(request):
    UserChapterRecord.objects.filter(account=request.user).update(cleared=False)
    UserLevelRecord.objects.filter(account=request.user).update(cleared=False)
    UserLineRecord.objects.filter(account=request.user).update(cleared=False)
    UserQuestionRecord.objects.filter(account=request.user).update(correct_count=0, answered_count=0, cleared=False)
    UserHintRecord.objects.filter(account=request.user).update(cleared=False)
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

        # 檢查是否作答正確
        is_correct = (user_answer == question.answer)

    elif question_type == "blue_crack":
        try:
            question = QuestionBlue.objects.get(id=question_id)
            record = UserQuestionRecord.objects.get(account=user, question_blue=question)
        except (QuestionBlue.DoesNotExist, UserQuestionRecord.DoesNotExist):
            return JsonResponse({"error": "Blue question not found"}, status=404)

        is_correct = (user_answer.strip() == question.answer.strip())

    elif question_type == "big_crack":
        try:
            question = QuestionBig.objects.get(id=question_id)
            record = UserQuestionRecord.objects.get(account=user, question_big=question)
        except (QuestionBig.DoesNotExist, UserQuestionRecord.DoesNotExist):
            return JsonResponse({"error": "Big question not found"}, status=404)

        # 檢查是否作答正確
        is_correct = (user_answer == question.answer)

    else:
        return JsonResponse({"error": "Invalid question type"}, status=400)

    record.answered_count += 1
    if is_correct:
        record.correct_count += 1
        record.cleared = True
    record.save()

    level = question.level
    chapter = question.chapter

    set_level_cleared(user, level)
    set_chapter_cleared(user, chapter)

    return JsonResponse({
        "question_id": question_id,
        "is_correct": is_correct,
        "message": "✅ 答對了！" if is_correct else "❌ 答錯了！",
        "game_over": check_all_cleared(user)
    })

# 確定所有都cleared
def check_all_cleared(user):
    all_lines_cleared = all(r.cleared for r in UserLineRecord.objects.all() if r.account == user)
    all_red_cleared = all(r.cleared for r in UserQuestionRecord.objects.all() if r.account == user and r.question_red)
    all_blue_cleared = all(r.cleared for r in UserQuestionRecord.objects.all() if r.account == user and r.question_blue)
    all_big_cleared = all(r.cleared for r in UserQuestionRecord.objects.all() if r.account == user and r.question_big)
    all_chapters_cleared = all(r.cleared for r in UserChapterRecord.objects.all() if r.account == user)
    all_levels_cleared = all(r.cleared for r in UserLevelRecord.objects.all() if r.account == user)

    return all([all_lines_cleared, all_red_cleared, all_blue_cleared, all_big_cleared, all_chapters_cleared, all_levels_cleared])

# 設定章節通
def set_chapter_cleared(user, chapter):
    """
    檢查該使用者是否完成此章節內所有對話與紅藍題，完成則標記 cleared。
    """
    # 檢查章節內對話是否完成
    user_lines = UserLineRecord.objects.filter(cleared=False, account=user, line__chapter=chapter)
    if user_lines.exists():
        return False

    # 檢查章節內紅藍題是否完成
    user_red_questions = UserQuestionRecord.objects.filter(cleared=False, account=user, question_red__chapter=chapter)
    user_blue_questions = UserQuestionRecord.objects.filter(cleared=False, account=user, question_blue__chapter=chapter)
    user_big_questions = UserQuestionRecord.objects.filter(cleared=False, account=user, question_big__chapter=chapter)

    if user_red_questions.exists() or user_blue_questions.exists() or user_big_questions.exists():
        return False

    UserChapterRecord.objects.update_or_create(
        account=user, chapter=chapter, defaults={'cleared': True})
    return True

def set_level_cleared(user, level):
    """
    檢查該使用者是否完成此關卡所有紅藍題，若都完成則標記 cleared。
    """
    # 1) 若需要檢查關卡內所有對話 => 先查： lines = Line.objects.filter(chapter=level.chapter)
    #    (前提：Level 有 foreign key 到 Chapter)
    user_lines = UserLineRecord.objects.filter(
        cleared=False, account=user, line__level=level)
    if user_lines.exists():
        return False

    # 2) 查詢所有尚未完成的紅/藍題（屬於此 level 的）
    user_red_questions = UserQuestionRecord.objects.filter(cleared=False, account=user, question_red__level=level)
    user_blue_questions = UserQuestionRecord.objects.filter(cleared=False, account=user, question_blue__level=level)
    user_big_questions = UserQuestionRecord.objects.filter(cleared=False, account=user, question_big__level=level)

    # 如果還有未完成的題目，就不標記通關
    if user_red_questions.exists() or user_blue_questions.exists() or user_big_questions.exists():
        return False

    # 3) 若真的都完成，標記此關卡為通關
    UserLevelRecord.objects.update_or_create(account=user, level=level, defaults={'cleared': True})

    return True

# ✅ 取得最小尚未通關的關卡（依 Level.id 最小）
def get_min_not_cleared_level(request):
    user = request.user

    # 找到所有未通關的關卡紀錄
    for level_record in UserLevelRecord.objects.filter(account=user, cleared=False):
        # 直接傳 Level 物件給 set_level_cleared
        set_level_cleared(user, level_record.level)

    remaining = UserLevelRecord.objects.filter(account=user, cleared=False).order_by('level__id')
    if remaining.exists():
        return JsonResponse({'level_name': remaining.first().level.level_name})

    # 全部完成後的處理: (可選擇 reset_game 或其他邏輯)
    first = UserLevelRecord.objects.filter(account=user).order_by('level__id').first()
    return JsonResponse({'level_name': first.level.level_name if first else 'Equality'})

# ✅ 取得最小尚未通關的章節（依 Chapter.chapter_id）
def get_min_not_cleared_chapter(request):
    user = request.user

    for chapter_record in UserChapterRecord.objects.filter(account=user, cleared=False):
        set_chapter_cleared(user, chapter_record.chapter)  # ✅ 傳物件而非 ID

    remaining = UserChapterRecord.objects.filter(account=user, cleared=False).order_by('chapter__chapter_id')
    if remaining.exists():
        return JsonResponse({'chapter_id': remaining.first().chapter.chapter_id})

    # 全部完成：可選擇重置
    first = UserChapterRecord.objects.filter(account=user).order_by('chapter__chapter_id').first()
    return JsonResponse({'chapter_id': first.chapter.chapter_id if first else 1})

def get_cutscene_info(request):
    user = request.user
    try:
        chapter_id = int(request.GET.get("chapter_id"))
        level_name = request.GET.get("level_name")
    except (TypeError, ValueError):
        return JsonResponse({"error": "Invalid parameters"}, status=400)

    try:
        chapter = Chapter.objects.get(chapter_id=chapter_id)
        level = Level.objects.get(level_name=level_name)
    except (Chapter.DoesNotExist, Level.DoesNotExist):
        return JsonResponse({"error": "Chapter or Level not found"}, status=404)

    try:
        speaker = Character.objects.get(name="player")
        listener = Character.objects.get(name="video")
    except Character.DoesNotExist:
        return JsonResponse({"error": "Characters 'player' or 'video' not defined."}, status=404)

    # 若題目尚未完成，不給動畫
    questions_pending = UserQuestionRecord.objects.filter(
        account=user,
        cleared=False,
        question_red__chapter=chapter,
        question_red__level=level,
    ) | UserQuestionRecord.objects.filter(
        account=user,
        cleared=False,
        question_blue__chapter=chapter,
        question_blue__level=level,
    ) | UserQuestionRecord.objects.filter(
        account=user,
        cleared=False,
        question_big__chapter=chapter,
        question_big__level=level,
    )

    if questions_pending.exists():
        return JsonResponse({"play_video": False})

    # 找出是否有對應的 line 且尚未 cleared
    cutscene_lines = Line.objects.filter(
        speaker=speaker,
        listener=listener,
        chapter=chapter,
        level=level
    )

    for line in cutscene_lines:
        record, created = UserLineRecord.objects.get_or_create(account=user, line=line)
        if not record.cleared:
            record.cleared = True
            record.save()
            filename = f"chapter{chapter.chapter_id}_{level.level_name}.mp4"
            return JsonResponse({"play_video": True, "video_url": f"/static/video/{filename}"})

    return JsonResponse({"play_video": False})

def get_remaining_questions(request):
    user = request.user
    crack_name = request.GET.get("crack_name")

    if not crack_name:
        return JsonResponse({"error": "缺少裂縫名稱"}, status=400)

    # Y：這個裂縫總共有幾題（全體）
    red_total = QuestionRed.objects.filter(map_object_name=crack_name).count()
    blue_total = QuestionBlue.objects.filter(map_object_name=crack_name).count()
    big_total = QuestionBig.objects.filter(map_object_name=crack_name).count()
    total = red_total + blue_total + big_total

    # X：這個使用者已經 cleared=True 的數量
    red_cleared = UserQuestionRecord.objects.filter(
        account=user, question_red__map_object_name=crack_name, cleared=True
    ).count()
    blue_cleared = UserQuestionRecord.objects.filter(
        account=user, question_blue__map_object_name=crack_name, cleared=True
    ).count()
    big_cleared = UserQuestionRecord.objects.filter(
        account=user, question_big__map_object_name=crack_name, cleared=True
    ).count()

    cleared = red_cleared + blue_cleared + big_cleared
    remaining = total - cleared

    return JsonResponse({
        "total": total,      # Y
        "cleared": cleared,  # Y - X
        "remaining": remaining  # X
    })

def get_remaining_cracks(request):
    user = request.user

    # 取得所有未完成的題目記錄（紅、藍、或大裂縫）
    uncleared_records = UserQuestionRecord.objects.filter(account=user)

    # 收集尚未完成的 map_object_name
    uncleared_cracks = set()

    for record in uncleared_records:
        if record.question_red and record.question_red.map_object_name:
            uncleared_cracks.add(record.question_red.map_object_name)
        elif record.question_blue and record.question_blue.map_object_name:
            uncleared_cracks.add(record.question_blue.map_object_name)
        elif record.question_big and record.question_big.map_object_name:
            uncleared_cracks.add(record.question_big.map_object_name)

    return JsonResponse({"remaining_cracks": len(uncleared_cracks)})

@login_required
def get_hint_content(request):
    user = request.user
    chapter_id = request.GET.get('chapter_id')
    level_name = request.GET.get('level_name')
    speaker = request.GET.get('speaker')
    listener = request.GET.get('listener')

    if not chapter_id or not level_name or not speaker or not listener:
        return JsonResponse({'hint': '目前無提示'}, status=200)

    try:
        chapter = Chapter.objects.get(chapter_id=chapter_id)
        level = Level.objects.get(level_name=level_name)
        speaker_obj = Character.objects.get(name=speaker)
        listener_obj = Character.objects.get(name=listener)
    except (Chapter.DoesNotExist, Level.DoesNotExist, Character.DoesNotExist):
        return JsonResponse({'hint': '資料錯誤'}, status=404)

    hint = Hint.objects.filter(
        chapter=chapter,
        level=level,
        speaker=speaker_obj,
        listener=listener_obj
    ).first()

    if hint:
        UserHintRecord.objects.update_or_create(
            account=user,
            hint=hint,
            defaults={"cleared": True}
        )
        return JsonResponse({'hint': hint.hint_content})

    return JsonResponse({'hint': '目前無提示'})

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
    all_big_cleared = all(r.cleared for r in UserQuestionRecord.objects.all() if r.account == user and r.question_big)
    all_chapters_cleared = all(r.cleared for r in UserChapterRecord.objects.all() if r.account == user)
    all_levels_cleared = all(r.cleared for r in UserLevelRecord.objects.all() if r.account == user)

    if all([all_lines_cleared, all_red_cleared, all_blue_cleared, all_chapters_cleared, all_levels_cleared]):
        UserLineRecord.objects.filter(account=user).update(cleared=False)
        UserQuestionRecord.objects.filter(account=user).update(cleared=False)
        UserChapterRecord.objects.filter(account=user).update(cleared=False)
        UserLevelRecord.objects.filter(account=user).update(cleared=False)

    try:
        # chapter_id = int(chapter_id)
        chapter = Chapter.objects.get(chapter_id=chapter_id)
        level = Level.objects.get(level_name=level_name)
    except (Chapter.DoesNotExist, Level.DoesNotExist):
        return JsonResponse({'error': 'Invalid chapter_id or level_name'}, status=404)

    flows = ChapterFlow.objects.filter(
        chapter=chapter, level=level).order_by('order')

    # 取使用者紀錄（不用 filter）
    cleared_lines = [r.line.id for r in UserLineRecord.objects.filter(account=request.user, cleared=True, line__isnull=False)]
    cleared_red = [r.question_red.id for r in UserQuestionRecord.objects.filter(account=request.user, cleared=True, question_red__isnull=False)]
    cleared_blue = [r.question_blue.id for r in UserQuestionRecord.objects.filter(account=request.user, cleared=True, question_blue__isnull=False)]
    cleared_big = [r.question_big.id for r in UserQuestionRecord.objects.filter(account=request.user, cleared=True, question_big__isnull=False)]

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
        
        elif flow.question_big and flow.question_big.id not in cleared_big:
            if flow.question_big.listener and flow.question_big.listener.name == listener:
                flow_list.append({
                    "type": "big_crack",
                    "id": flow.question_big.id,
                    "question": flow.question_big.question,
                    "option1": flow.question_big.option1,
                    "option2": flow.question_big.option2,
                    "option3": flow.question_big.option3,
                    "option4": flow.question_big.option4,
                    "answer": flow.question_big.answer,
                    "correct": flow.question_big.correct,
                })
                # UserQuestionRecord.objects.update_or_create(account=request.user, question_big=flow.question_big, defaults={'cleared': True})

    if not flow_list:
        flow_list.append({"type": "line", "content": "沒有對話內容。"})

    return JsonResponse({'flow': flow_list})