from enum import Enum

from openAiChat.common.exception.CustomException import CustomException
from openAiChat.common.exception.ErrorCode import ErrorCode


class OpenAPIKeyEnum(Enum):
    DEEPSEEK = ("deepseek", "sk-0da03bdfd5414766ae05a0050134cfb1", 'https://api.deepseek.com')

    # 模型厂商
    @property
    def model_source(self):
        return self.value[0]

    # 接口 api_key
    @property
    def api_key(self):
        return self.value[1]

    # 调用 url
    @property
    def base_url(self):
        return self.value[2]

    @classmethod
    def get_enum_by_model_source(cls, model_source):
        if not model_source:
            raise CustomException(ErrorCode.PARAMS_EMPTY_ERROR.code, ErrorCode.PARAMS_EMPTY_ERROR.errmsg)
        for enum in cls:
            if enum.model_source == model_source:
                return enum
        raise CustomException(ErrorCode.ENUM_NOT_FIND_ERROR.code, ErrorCode.ENUM_NOT_FIND_ERROR.errmsg(enum_name=model_source))


