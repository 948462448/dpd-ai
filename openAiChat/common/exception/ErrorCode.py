from enum import Enum
import json


class ErrorCode(Enum):
    OK = ("200", '成功')

    SERVER_ERR = ("500", '服务器异常')

    # 0000 通用错误
    REQUEST_TYPE_NO_SUPPORT_ERROR = ("0000001", "请求协议不支持")
    QUERY_DATA_NO_EXISTS_ERROR = ("0000002", "数据未找到")
    PARAMS_EMPTY_ERROR = ("0000003", "参数为空")
    ENUM_NOT_FIND_ERROR = ("0000004", "未匹配到对应枚举 {enum_name}")
    # 0001 auth错误
    USER_NOT_LOGGED_IN_ERROR = ("0001001", "用户未登录")
    USER_EXIST_ERROR = ("00001002", "用户已存在")
    USER_AUTH_ERROR = ("00001003", "用户认证失败")
    USER_NOT_EXIST_ERROR = ("00001004", "用户不存在，请确认")
    USER_NO_PERMISSION_ERROR = ("00001005", "无权限")


    @property
    def code(self):
        """获取状态码"""
        return self.value[0]

    @property
    def errmsg(self, **kwargs):
        """获取状态码信息"""
        return self.value[1].format(**kwargs)

    @property
    def error_print(self, **kwargs):
        error = {
            "code": self.code,
            "msg": self.errmsg.format(**kwargs),
            "success": True if self.code == "200" else False
        }
        return error
