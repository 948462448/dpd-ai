from enum import Enum

from openAiChat.common.exception.CustomException import CustomException
from openAiChat.common.exception.ErrorCode import ErrorCode


class SupportModelEnum(Enum):
    DEEPSEEK_CHAT = ("deepseek-chat", "通用对话V2", "deepseek")
    DEEPSEEK_CODE = ("deepseek-code", "代码助手V2", "deepseek")

    # 模型名字
    @property
    def model_name(self):
        return self.value[0]

    # 模型中文名
    @property
    def model_name_zh(self):
        return self.value[1]

    # 模型来源
    @property
    def model_source(self):
        return self.value[2]

    @classmethod
    def get_enum_source_by_model_name(cls, model_name):
        if not model_name:
            raise CustomException(ErrorCode.PARAMS_EMPTY_ERROR.code, ErrorCode.PARAMS_EMPTY_ERROR.errmsg)
        for model_enum in cls:
            if model_enum.model_name == model_name:
                return model_enum.model_source
        raise CustomException(ErrorCode.ENUM_NOT_FIND_ERROR.code, ErrorCode.ENUM_NOT_FIND_ERROR.errmsg(model_name=model_name))

    @classmethod
    def get_all_model(cls):
        support_model_list = []
        for model_enum in cls:
            support_model_list.append(model_enum.model_name)

        return support_model_list

