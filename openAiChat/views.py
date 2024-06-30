from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Article
from openai import OpenAI

api_key = "sk-0da03bdfd5414766ae05a0050134cfb1"
base_url = "https://api.deepseek.com"

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


@csrf_exempt
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
