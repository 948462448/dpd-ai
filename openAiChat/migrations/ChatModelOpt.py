from openAiChat.models import ChatList

"""
保存或更新
"""


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
