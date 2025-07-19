import functools
from datetime import datetime
import ddddocr
import logging
import sys
from pathlib import Path
from err import RetryableError
import time

_ocr = ddddocr.DdddOcr(show_ad=False)


LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)

log_file = LOG_DIR / 'app.log'
log_file.write_text('')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s | %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger('jeecg_bot')


def retry(
    *,
    max_times: int = 3,
    on_errors: tuple[type[Exception], ...] = (RetryableError,),
    backoff: float = 1,
):
    """通用重试装饰器"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_times + 1):
                try:
                    return func(*args, **kwargs)
                except on_errors as exc:
                    if attempt == max_times:
                        logger.exception('达到最大重试次数，放弃')
                        raise
                    sleep = backoff * (2 ** (attempt - 1))
                    logger.warning(
                        f'{func.__name__} 第 {attempt} 次失败: {exc}，{sleep}s 后重试'
                    )
                    time.sleep(sleep)

        return wrapper

    return decorator


def format_time_with_today(hour: int) -> str:
    """
    输入 0-23 数
    输出指定日期格式
    """

    now = datetime.now()

    try:
        if hour < 0 or hour > 23:
            raise ValueError('小时必须在0-23之间')
    except ValueError as e:
        return f'输入无效: {e}'

    today_with_hour = datetime(now.year, now.month, now.day, hour)

    return today_with_hour.strftime('%Y-%m-%d %H:%M:%S')


def recognize_captcha(path: str) -> str:
    with open(path, 'rb') as f:
        img_bytes = f.read()
    text = _ocr.classification(img_bytes)
    if not text:  # 识别为空
        return input(f'识别为空，请人工输入 {path} 中的验证码：')
    return text
