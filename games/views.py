from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import Http404

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