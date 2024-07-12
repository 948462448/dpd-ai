from django.urls import path
from django.views.generic import TemplateView

from .view import ChatViews, AuthView

urlpatterns = [
    # 鉴权
    path("api/v1/get/token", AuthView.get_csrf_token, name="get_token"),
    path('', TemplateView.as_view(template_name='index.html')),
    path('api/v1/register', AuthView.register, name='register'),
    path('api/v1/login', AuthView.login_view, name='login'),
    path('api/v1/logout', AuthView.logout_view, name='logout'),
    path('api/v1/check/login', AuthView.check_user_login, name='checkLogin'),

    # 聊天
    path("api/v1/chat/get", ChatViews.deepseek_ai_chat_v1, name="deepseek_ai_chat_v1"),
    path("api/v2/batch/chat", ChatViews.deepseek_ai_chat_v2, name="deepseek_ai_chat_v2"),
    path("api/v3/stream/chat", ChatViews.deepseek_ai_chat_v3, name="deepseek_ai_chat_v3"),

    path('api/v1/get/chat/list', ChatViews.get_chat_record_list, name='doGetChatRecordList'),
    path('api/v1/chat/rename', ChatViews.chat_record_rename, name='doRenameChatRecord'),
    path('api/v1/get/chat/one', ChatViews.get_chat_record, name='doGetChatListOne'),
    path('api/v1/chat/flush', ChatViews.do_flush_chat_record_list, name='doGetFlushChatRecordList'),
]
