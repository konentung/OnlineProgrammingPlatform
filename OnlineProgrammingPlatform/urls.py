"""
URL configuration for OnlineProgrammingPlatform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
import posts.views as questions_views
from accounts.views import custom_404_view

handler404 = custom_404_view

urlpatterns = [
    path('admin/', admin.site.urls),
    # ----------------- accounts -----------------
    path('', accounts_views.index, name='Index'),
    path('login/', accounts_views.sign_in, name='Login'),
    path('logout/', accounts_views.log_out, name='Logout'),
    path('register/', accounts_views.register, name='Register'),
    
    # ----------------- questions -----------------
    path('question/<int:pk>/', questions_views.question_detail, name='QuestionDetail'),
    path('question/create/', questions_views.question_create, name='QuestionCreate'),
    path('question/update/<int:pk>/', questions_views.question_update, name='QuestionUpdate'),
    path('question/delete/<int:pk>/', questions_views.question_delete, name='QuestionDelete'),
    path('question/assignment/', questions_views.question_assignment_list, name='QuestionAssignment'),
    path('question/answer/<int:pk>/', questions_views.question_answer, name='QuestionAnswer'),
    path('question/history/', questions_views.user_question_history_list, name='UserQuestionHistoryList'),
    path('question/history/<int:question_id>/', questions_views.question_history_list, name='QuestionHistoryList'),
    path('question/peer_assessment/', questions_views.peer_assessment_list, name='PeerAssessmentList'),
    path('peer-assessment/<int:question_id>/', questions_views.peer_assessment, name='PeerAssessment'),
]