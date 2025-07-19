class BizError(Exception):
    """业务已知异常，触发降级或给用户友好提示"""

    pass


class LoginExpired(BizError):
    """登录失效"""

    pass


class RetryableError(Exception):
    """网络抖动、验证码识别失败等可重试错误"""

    pass
