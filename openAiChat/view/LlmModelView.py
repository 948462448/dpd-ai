import json

from django.http import JsonResponse

from openAiChat.service import LlmModelService

"""
获取当前已经接入的模型列表
"""


def get_support_llm_model(request):
    llm_model_list = LlmModelService.get_llm_model_list()
    json_response = {
        "success": True,
        "code": 200,
        "data": json.dumps(llm_model_list)
    }
    return JsonResponse(json_response)
