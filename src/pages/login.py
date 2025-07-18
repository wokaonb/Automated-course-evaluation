from playwright.sync_api import Page

from config import BASE_URL
from utils import recognize_captcha


class LoginPage:
    def __init__(self, page: Page) -> None:
        self.page = page

    # 访问登录页
    def get_captcha(self, captcha_path: str) -> bytes:
        self.page.goto(BASE_URL)
        captcha = self.save_captcha(captcha_path)
        return captcha

    # 登录主流程
    def login(self, username: str, password: str) -> None:
        for _ in range(3):
            # 获取并识别验证码
            captcha_path = 'captcha.png'
            self.get_captcha(captcha_path)
            code = recognize_captcha(captcha_path)

            # 填表并登录
            self.page.get_by_placeholder('请输入帐户名').fill(username)
            self.page.get_by_placeholder('请输入密码').fill(password)
            self.page.get_by_placeholder('请输入验证码').fill(code)
            self.page.get_by_role('button', name='确 定').click()

            # 等待跳转，判断是否仍在登录页
            self.page.wait_for_timeout(1000)
            if not self.page.get_by_role('link', name='logoJeecg Boot').count():
                return  # 登录成功

        raise RuntimeError('验证码错误')

    # 保存验证码图片
    def save_captcha(self, path: str = 'captcha.png') -> bytes:
        return (
            self.page.get_by_role('tabpanel').get_by_role('img').screenshot(path=path)
        )
