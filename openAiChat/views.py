import json

from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login, logout
from openai import OpenAI

from openAiChat.common.exception.ErrorCode import ErrorCode

api_key = "sk-0da03bdfd5414766ae05a0050134cfb1"
base_url = "https://api.deepseek.com"


def get_csrf_token(request):
    token = get_token(request)
    return JsonResponse({'token': token})


# 对话V1版本，仅支持一条提问，不支持对话
def deepseek_ai_chat_v1(request):
    client = OpenAI(api_key=api_key, base_url=base_url)
    message = request.GET.get('msg')
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system",
             "content": "你是一个很有帮助的私人助理，知识面很广泛。可以回答用户提出的各种问题。不过记住一点，对于对话中已经回答过的问题，就不要再回答了。专注于新的问题解答即可"},
            {"role": "user", "content": f'{message}'},
        ],
        presence_penalty=1.5,
        stream=False
    )
    return HttpResponse(response.choices[0].message.content)


# 对话V2版本，支持多轮对话提问
def deepseek_ai_chat_v2(request):
    client = OpenAI(api_key=api_key, base_url=base_url)
    message_dirt = eval(request.body)
    message_list = message_dirt["msg"]
    request_param = [{"role": "system", "content": "You are a helpful assistant"}]
    for param in message_list:
        request_param.append({"role": param["role"], "content": param["content"]})

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=request_param,
        stream=False
    )
    return HttpResponse(response.choices[0].message.content)


def register(request):
    if request.method == 'POST':
        # 获取参数
        user_name = request.POST.get('username', '')
        pwd = request.POST.get('password', '')

        # 用户已存在
        if User.objects.filter(username=user_name):
            return JsonResponse(ErrorCode.USER_EXIST_ERROR.error_print)
        # 用户不存在
        else:
            # 使用User内置方法创建用户
            user = User.objects.create_user(
                username=user_name,
                password=pwd,
                email='123@qq.com',
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


def login(request):
    if request.method == 'POST':
        # 获取参数
        user_name = request.POST.get('username', '')
        pwd = request.POST.get('password', '')

        # 用户已存在
        if User.objects.filter(username=user_name):
            # 使用内置方法验证
            user = authenticate(username=user_name, password=pwd)
            # 验证通过
            if user:
                return JsonResponse({
                    'code': 200,
                    'success': True,
                    'msg': '登录成功'
                })
            # 验证失败
            else:
                return JsonResponse(ErrorCode.USER_AUTH_ERROR.error_print)

        # 用户不存在
        else:
            return JsonResponse(ErrorCode.REQUEST_TYPE_NO_SUPPORT_ERROR.error_print)


"""此处导入的模块和注册是一样的"""


def logout(request):
    logout(request)
    return JsonResponse({
        'code': 200,
        'success': True,
        'msg': '用户已登出'
    })
