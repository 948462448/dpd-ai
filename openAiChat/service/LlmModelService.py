from openAiChat.common.enums.SupportModelEnum import SupportModelEnum


def get_llm_model_list():
    return SupportModelEnum.get_all_model()
