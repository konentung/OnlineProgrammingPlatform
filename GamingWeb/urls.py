"""
URL configuration for GamingWeb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import accounts.views as accounts_views
import games.views as games_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # accounts
    path('', accounts_views.index, name='Index'),
    path('accounts/login/', accounts_views.sign_in, name='Login'),
    path('accounts/logout/', accounts_views.log_out, name='Logout'),
    path('accounts/register/', accounts_views.register, name='Register'),
    
    # games
    path('about/', games_views.about, name='About'),
    path('game/', games_views.game, name='Game'),
    path('notes/', games_views.notes, name='Notes'),
    path('notes/<str:unit_name>', games_views.note_content, name='NoteContent'),
    path('api/chapter/', games_views.get_min_not_cleared_chapter),
    path('api/chapterflow/', games_views.get_chapter_flow, name='ChapterFlow'),
    path('api/level/', games_views.get_min_not_cleared_level),
    path('api/line/', games_views.get_min_not_cleared_line),
    path('api/check/', games_views.check_answer),
    
    path('api/reset/', games_views.reset_game),
    
    # ai
    
]

if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)