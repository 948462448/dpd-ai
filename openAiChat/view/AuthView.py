import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http import require_http_methods

from openAiChat.common.exception.ErrorCode import ErrorCode


def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({
        'code': 200,
        'success': True,
        'token': token
    })


def check_user_login(request):
    return JsonResponse({
        'code': 200,
        'success': True,
        'data': request.user.is_authenticated
    })


def register(request):
    if request.method == 'POST':
        # 获取参数
        user_name = json.loads(request.body).get('username', '')
        pwd = json.loads(request.body).get('password', '')

        # 用户已存在
        if User.objects.filter(username=user_name):
            return JsonResponse(ErrorCode.USER_EXIST_ERROR.error_print)
        # 用户不存在
        else:
            # 使用User内置方法创建用户
            user = User.objects.create_user(
                username=user_name,
                password=pwd,
                is_staff=1,
                is_active=1,
                is_superuser=0
            )

            return JsonResponse({
                'code': 200,
                'msg': '用户注册成功',
                'success': True
            })

    else:
        return JsonResponse(ErrorCode.REQUEST_TYPE_NO_SUPPORT_ERROR.error_print)


@require_http_methods(["POST"])
def login_view(request):
    # 获取参数
    user_name = json.loads(request.body).get('username', '')
    pwd = json.loads(request.body).get('password', '')
    # 用户已存在
    if User.objects.filter(username=user_name):
        # 使用内置方法验证
        user = authenticate(username=user_name, password=pwd)
        # 验证通过
        if user:
            login(request, user)
            return JsonResponse({
                'code': 200,
                'success': True,
                'msg': '登录成功',
                'data': {
                    'username': user.username
                }
            })
        # 验证失败
        else:
            return JsonResponse(ErrorCode.USER_AUTH_ERROR.error_print)
    else:
        return JsonResponse(ErrorCode.USER_NOT_EXIST_ERROR.error_print)


@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return JsonResponse({
        'code': 200,
        'success': True,
        'msg': '用户已登出'
    })
