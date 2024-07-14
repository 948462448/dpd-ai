import json

from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.core import serializers

from django.views.decorators.http import require_http_methods
from openai import OpenAI

from openAiChat.common.enums.SupportModelEnum import SupportModelEnum
from openAiChat.common.exception.ErrorCode import ErrorCode
from openAiChat.models import ChatList
from openAiChat.service import ChatService


# 对话V1版本，仅支持一条提问，不支持对话
def chat_v1(request):
    client = OpenAI(api_key="", base_url="")
    message = request.GET.get('msg')
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system",
             "content": "你是一个很有帮助的私人助理，知识面很广泛。可以回答用户提出的各种问题。不过记住一点，对于对话中已经回答过的问题，就不要再回答了。专注于新的问题解答即可"},
            {"role": "user", "content": f'{message}'},
        ],
        presence_penalty=1.5,
        stream=True
    )
    return HttpResponse(response)


# 对话V2版本，支持多轮对话提问
@require_http_methods(["POST"])
def chat_v2(request):
    chat_id, history_message_list, message_list, model, uuid = do_get_chat_param(request)
    answer_json = ChatService.batch_chat(chat_id, message_list, history_message_list, model, request.user, uuid)
    json_response = {
        "success": True,
        "code": 200,
        "data": json.dumps(answer_json)
    }
    return JsonResponse(json_response)


@require_http_methods(["POST"])
def chat_v3(request):
    chat_id, history_message_list, message_list, model, uuid = do_get_chat_param(request)
    ai_response = ChatService.stream_chat(chat_id, message_list, history_message_list, model, request.user, uuid)
    stream_response = StreamingHttpResponse(ai_response, content_type='text/event-stream')
    stream_response['Cache-Control'] = 'no-cache'
    return stream_response


@login_required
@require_http_methods(["POST"])
def chat_record_rename(request):
    request_body = json.loads(request.body)
    user = request.user
    title = request_body.get("title")
    if not title:
        return JsonResponse(ErrorCode.PARAMS_EMPTY_ERROR.error_print)
    old_chat_record = ChatList.objects.filter(pk=request_body.get("chatId"))
    if old_chat_record.exists():
        record = old_chat_record.first()
        if record.userId != user.username:
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
@require_http_methods(["POST"])
def chat_record_delete(request):
    request_body = json.loads(request.body)
    user = request.user
    old_chat_record = ChatList.objects.filter(pk=request_body.get("chatId"))
    if old_chat_record.exists():
        data = old_chat_record.first();
        if data.userId != user.username:
            return JsonResponse(ErrorCode.USER_NO_PERMISSION_ERROR.error_print)
        old_chat_record.delete()
        return JsonResponse({
            'code': 200,
            'success': True,
            'msg': '删除成功',
            'data': True
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


"""
    提取会话请求参数
"""


def do_get_chat_param(request):
    message_dirt = json.loads(request.body)
    message_list = message_dirt.get("msg", "")
    chat_id = message_dirt.get("chatId", "")
    history_message_list = message_dirt.get('historyChatList', "")
    model = message_dirt.get('model', SupportModelEnum.DEEPSEEK_CHAT.model_name)
    uuid = message_dirt.get('uuid', "")
    return chat_id, history_message_list, message_list, model, uuid
