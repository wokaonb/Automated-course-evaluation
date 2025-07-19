import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from utils import logger
from config import USER_NAME, USER_PASSWORD
from pages import CourseManagement, LoginPage
from model import CourseModel
from err import BizError, LoginExpired


def run() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(
            viewport={
                'width': 1280,
                'height': 720,
            },
            locale='zh-CN',
        )
        context.set_default_timeout(15000)
        with context.new_page() as cur_page:
            login_page = LoginPage(cur_page)
            login_page.login(USER_NAME, USER_PASSWORD)

        courses_raw = json.loads(Path('courses.json').read_text(encoding='utf-8'))
        courses = [CourseModel(**course_raw) for course_raw in courses_raw]

        for course in courses:
            with context.new_page() as cur_page:
                manager_page = CourseManagement(cur_page)
                cur_page.pause()
                manager_page.add_schedule(
                    course.code,
                    course.progress,
                    course.time[0],
                    course.time[1],
                    course.state,
                    course.content,
                )

                manager_page.set_users_over(
                    course.code,
                    course.progress,
                    course.users_over,
                )
                manager_page.set_users_leave(
                    course.code,
                    course.progress,
                    course.users_leave,
                )

                manager_page.set_user_state_discusses(
                    course.code,
                    course.progress,
                    course.content,
                    course.discuss_content,
                    course.users_over,
                    course.discuss_state,
                )

        browser.close()


if __name__ == '__main__':
    try:
        run()
    except LoginExpired:
        logger.error('登录已失效，人工检查账号或验证码逻辑')
    except BizError as e:
        logger.error(f'业务异常: {e}')
    except Exception:
        logger.exception('未知异常，需人工介入')
