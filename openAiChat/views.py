import json

from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core import serializers

from django.views.decorators.http import require_http_methods
from openai import OpenAI

from openAiChat.common.exception.ErrorCode import ErrorCode
from openAiChat.models import ChatList

api_key = "sk-0da03bdfd5414766ae05a0050134cfb1"
base_url = "https://api.deepseek.com"


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
@require_http_methods(["POST"])
def deepseek_ai_chat_v2(request):
    client = OpenAI(api_key=api_key, base_url=base_url)
    message_dirt = json.loads(request.body)
    message_list = message_dirt["msg"]
    chat_id = message_dirt["chatId"]
    request_param = [{"role": "system", "content": "You are a helpful assistant"}]
    for param in message_list:
        request_param.append({"role": param["role"], "content": param["content"]})
    chat_id = save_chat_record(chat_id, request.user, json.dumps(message_dirt['historyChatList'], ensure_ascii=False), "deepseek-chat",
                               message_list[0]["content"])
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=request_param,
        stream=False
    )
    request_param.append({"role": response.choices[0].message.role,
                          "content": response.choices[0].message.content})
    request_param.pop(0)
    message_dirt['historyChatList'].append({"role": response.choices[0].message.role,
                                            "content": response.choices[0].message.content, "type": "chat"})
    chat_id = save_chat_record(chat_id, request.user, json.dumps(message_dirt['historyChatList'], ensure_ascii=False), "deepseek-chat",
                               message_list[0]["content"])
    json_response = {
        "success": True,
        "code": 200,
        "data": {
            "id": chat_id,
            "message": response.choices[0].message.content
        }
    }
    return JsonResponse(json_response)


@login_required
@require_http_methods(["POST"])
def chat_record_rename(request):
    request_body = json.loads(request.body)
    user = request.user
    old_chat_record = ChatList.objects.filter(pk=request_body.get("chatId")).first()
    if old_chat_record.exists():
        if old_chat_record.userId != user.username:
            return JsonResponse(ErrorCode.USER_NO_PERMISSION_ERROR.error_print)
        old_chat_record.update(title=request_body.get("title"))
        return JsonResponse({
            'code': 200,
            'success': True,
            'msg': '更新成功',
            'data': request_body.get("title")
        })
    else:
        return JsonResponse(ErrorCode.QUERY_DATA_NO_EXISTS_ERROR.error_print)


@login_required
def get_chat_record_list(request):
    user = request.user
    top_20_objects = ChatList.objects.filter(userId=user.username).order_by('-gmt_modified')[0:20]
    json_data = serializers.serialize('json', top_20_objects.all())
    return JsonResponse({
        'code': 200,
        'success': True,
        'data': json_data
    })


@login_required
def get_chat_record(request):
    user = request.user
    chat_id = request.GET.get('chatId')
    chat_record_obj = ChatList.objects.filter(pk=chat_id, userId=user.username).first()
    json_data = serializers.serialize('json', chat_record_obj.first())
    return JsonResponse({
        'code': 200,
        'success': True,
        'data': json_data
    })


@login_required
@require_http_methods(["POST"])
def do_flush_chat_record_list(request):
    user = request.user
    request_body_res = json.loads(request.body)
    chat_id = request_body_res.get('chatId')
    message_list = json.dumps(request_body_res.get('historyChatList'), ensure_ascii=False)
    ChatList.objects.filter(pk=chat_id, userId=user.username).update(chat=message_list)
    return JsonResponse({
        'code': 200,
        'success': True,
        'data': "更新成功"
    })


def save_chat_record(chat_id, current_user, chat_record, model, title):
    if not chat_id:
        chat_record_obj = ChatList(userId=current_user.username,
                                   model=model,
                                   title=title,
                                   chat=chat_record)
        chat_record_obj.save()
        return chat_record_obj.id
    else:
        ChatList.objects.filter(pk=chat_id).update(chat=chat_record)
        return chat_id


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
