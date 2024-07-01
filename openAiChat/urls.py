from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("api/v1/chat/get", views.deepseek_ai_chat_v1, name="deepseek_ai_chat_v1"),
    path("api/v2/chat/get", views.deepseek_ai_chat_v2, name="deepseek_ai_chat_v2"),
    path('', TemplateView.as_view(template_name='index.html')),
    # 登录
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]
