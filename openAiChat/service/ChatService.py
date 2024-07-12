import json

from openai import OpenAI

from openAiChat.common.enums.OpenAPIKeyEnum import OpenAPIKeyEnum
from openAiChat.common.enums.SupportModelEnum import SupportModelEnum
from openAiChat.dal import ChatModelOpt

"""
   流式请求对话
   chat_id: 对话ID
   message_list: 当前对话列表
   history_chat_list: 历史对话列表
   model： 请求模型名
   """


def stream_chat(chat_id, message_list, history_chat_list, model, user, uuid):
    model_source = SupportModelEnum.get_enum_source_by_model_name(model)
    model_source_enum = OpenAPIKeyEnum.get_enum_by_model_source(model_source)
    client = OpenAI(api_key=model_source_enum.api_key, base_url=model_source_enum.base_url)
    request_param = [{"role": "system", "content": "You are a helpful assistant"}]
    for param in message_list:
        request_param.append({"role": param["role"], "content": param["content"]})
    chat_id = ChatModelOpt.save_chat_record(chat_id, user, json.dumps(history_chat_list, ensure_ascii=False),
                                            model, message_list[0]["content"])
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=request_param,
        stream=True
    )
    model_answer_messages = []
    role = ""
    for chunk in response:
        chunk_message = chunk.choices[0].delta.content  # extract the message
        model_answer_messages.append(chunk_message)  # save the message
        response_json = {
            "success": True,
            "code": 200,
            "data": {
                "chatId": chat_id,
                "message": chunk_message,
                "role": chunk.choices[0].delta.role,
                "finish": False,
            }
        }
        if not role:
            role = chunk.choices[0].delta.role
        """
            格式必须是 data: xxxx \n\n
        """
        if chunk.choices[0].finish_reason != "stop":
            yield 'data: %s\n\n' % json.dumps(response_json, ensure_ascii=False)

    response_json = {
        "success": True,
        "code": 200,
        "data": {
            "chatId": chat_id,
            "message": "",
            "role": "",
            "finish": True,
        }
    }
    model_answer_str = "".join(model_answer_messages)
    history_chat_list.append({"id": f'{uuid}_a', "role": role, "content": model_answer_str, "type": "chat"})
    ChatModelOpt.save_chat_record(chat_id, user, json.dumps(history_chat_list, ensure_ascii=False),
                                  model, message_list[0]["content"])
    yield 'data: %s\n\n' % json.dumps(response_json, ensure_ascii=False)


"""
    批请求
"""


def batch_chat(chat_id, message_list, history_chat_list, model, user, uuid):
    request_param = [{"role": "system", "content": "You are a helpful assistant"}]
    model_source = SupportModelEnum.get_enum_source_by_model_name(model)
    model_source_enum = OpenAPIKeyEnum.get_enum_by_model_source(model_source)
    client = OpenAI(api_key=model_source_enum.api_key, base_url=model_source_enum.base_url)
    for param in message_list:
        request_param.append({"role": param["role"], "content": param["content"]})
    chat_id = ChatModelOpt.save_chat_record(chat_id, user, json.dumps(history_chat_list, ensure_ascii=False), model,
                                            message_list[0]["content"])
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=request_param,
        stream=False
    )
    request_param.append({"role": response.choices[0].message.role,
                          "content": response.choices[0].message.content})
    history_chat_list.append({"id": f'{uuid}_a', "role": response.choices[0].message.role,
                              "content": response.choices[0].message.content, "type": "chat"})
    chat_id = ChatModelOpt.save_chat_record(chat_id, user, json.dumps(history_chat_list, ensure_ascii=False),
                                            model, message_list[0]["content"])
    answer_json = {
        "id": chat_id,
        "message": response.choices[0].message.content,
        "role": response.choices[0].message.role,
    }
    return answer_json
