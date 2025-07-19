from pathlib import Path
from playwright.sync_api import Page, TimeoutError as PWTimeout

from config import BASE_URL
from err import LoginExpired, RetryableError
from utils import recognize_captcha, retry, logging

logger = logging.getLogger('login_bot')


class LoginPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    # 登录主流程
    @retry(max_times=3, on_errors=(RetryableError, PWTimeout))
    def login(self, username: str, password: str) -> None:
        try:
            self.page.goto(BASE_URL, timeout=30_000)
        except PWTimeout as e:
            raise RetryableError('访问登录页超时') from e

        # 获取并识别验证码
        captcha_path = Path('captcha.png')
        try:
            self.page.get_by_role('tabpanel').get_by_role('img').screenshot(
                path=captcha_path
            )
            code = recognize_captcha(captcha_path)
        except Exception as e:
            logger.warning(f'验证码识别失败: {e}')
            raise RetryableError('验证码识别失败') from e

        # 填表并登录
        self.page.get_by_placeholder('请输入帐户名').fill(username)
        self.page.get_by_placeholder('请输入密码').fill(password)
        self.page.get_by_placeholder('请输入验证码').fill(code)
        self.page.get_by_role('button', name='确 定').click()

        # 判断是否登录成功
        self.page.wait_for_timeout(3000)
        if self.page.get_by_role('link', name='logoJeecg Boot').count():
            raise LoginExpired('登录失效，需重新登录')

        logger.info('登录成功')
