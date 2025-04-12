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
from games import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # accounts
    path('', accounts_views.index, name='Index'),
    path('login/', accounts_views.sign_in, name='Login'),
    path('logout/', accounts_views.log_out, name='Logout'),
    path('register/', accounts_views.register, name='Register'),

    # games
    path('about/', games_views.about, name='About'),
    path('game/', games_views.game, name='Game'),
    path('api/chapter/', games_views.get_min_not_cleared_chapter),
    path('api/chapterflow/', games_views.get_chapter_flow, name='ChapterFlow'),
    path('api/level/', games_views.get_min_not_cleared_level),
    path('api/check/', games_views.check_answer),
    path('api/get_cutscene_info/', games_views.get_cutscene_info),
    path('api/get_remaining_cracks/', games_views.get_remaining_cracks),
    path('api/get_remaining_questions/', games_views.get_remaining_questions),
    path('api/get_hint/', games_views.get_hint_content),
    path('api/reset/', games_views.reset_game),
    path('api/reset_all/', games_views.reset_user_all_game_data),
    # ai

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
