import json
from pathlib import Path
from playwright.sync_api import sync_playwright

from config import USER_NAME, USER_PASSWORD
from pages import CourseManagement, LoginPage
from model import CourseModel


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={
                'width': 1280,
                'height': 720,
            },
            locale='zh-CN',
        )

        cur_page = context.new_page()

        login_page = LoginPage(cur_page)
        login_page.login(USER_NAME, USER_PASSWORD)

        manager_page = CourseManagement(cur_page)

        courses_raw = json.loads(Path('courses.json').read_text(encoding='utf-8'))
        courses = [CourseModel(**course_raw) for course_raw in courses_raw]

        for course in courses:
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
    run()
