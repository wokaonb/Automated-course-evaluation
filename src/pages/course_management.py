from typing import Literal
from playwright.sync_api import Page, TimeoutError as PWTimeout
import re
from config import MANAGER_URL
from err import BizError
from utils import format_time_with_today, logging
from pydantic import validate_call

logger = logging.getLogger('manage_bot')


class CourseManagement:
    def __init__(self, page: Page):
        self.page = page

    ALLOWED_MANAGEMENT = Literal[
        '试听课登记表',
        '学生知识点矩阵展示',
        '课程人员',
        '课程进度',
        '课程进度人员',
        '课后反馈中心',
    ]

    @validate_call
    def to_management(self, to_name: ALLOWED_MANAGEMENT) -> None:
        """跳转指定目录"""
        self.page.goto(MANAGER_URL)
        self.page.locator('div').filter(has_text=re.compile(r'^课程管理$')).click()
        self.page.get_by_role('link', name=to_name, exact=True).click()

    ALLOWED_COURSE_STATE = Literal[
        '请选择',
        '无效',
        '未开始',
        '进行中',
        '已结束',
    ]

    @validate_call
    def add_progress(
        self,
        course_code: str,
        the_progress_of_the_curriculum: str,
        begin_time: int,
        end_time: int,
        course_state: ALLOWED_COURSE_STATE,
        course_content: str,
    ) -> None:
        """添加班级进度"""
        try:
            self.to_management('课程进度')

            self.page.get_by_role('button', name='图标: plus 新增').click()

            # 课程编号
            self.page.get_by_placeholder('请选择', exact=True).click()
            self.page.get_by_placeholder('请输入课程编码').fill(course_code)
            self.page.get_by_role('button', name='图标: search 查询').click()
            self.page.get_by_label('查询课程名称').get_by_role(
                'cell', name=course_code
            ).click()
            self.page.get_by_label('查询课程名称').get_by_role(
                'button', name='确 定'
            ).click()

            # 课程进度
            self.page.get_by_placeholder('请输入课程进度').fill(
                the_progress_of_the_curriculum
            )

            # 开始时间
            begin_time = format_time_with_today(begin_time)
            self.page.get_by_placeholder('请选择开始时间').click()
            self.page.get_by_placeholder('请选择开始时间').nth(1).fill(begin_time)
            self.page.get_by_placeholder('请选择开始时间').nth(1).press('Enter')

            # 结束时间
            end_time = format_time_with_today(end_time)
            self.page.get_by_placeholder('请选择结束时间').click()
            self.page.get_by_placeholder('请选择结束时间').nth(1).fill(end_time)
            self.page.get_by_placeholder('请选择结束时间').nth(1).press('Enter')

            # 状态
            self.page.get_by_text('请选择状态').click()
            self.page.get_by_title(course_state).click()

            # 课程内容
            self.page.get_by_placeholder('请输入课程内容').fill(course_content)

            # 确定
            self.page.get_by_role('button', name='确 定').click()
            self.page.wait_for_load_state('networkidle')
            logger.info(
                f'{course_code}-{the_progress_of_the_curriculum} 课程进度添加成功'
            )
        except PWTimeout:
            raise BizError(
                f'{course_code}-{the_progress_of_the_curriculum} 课程进度添加失败'
            )

    def add_members(
        self,
        course_code: str,
        the_progress_of_the_curriculum: str,
    ) -> None:
        """批量增加班级人员"""
        try:
            self.to_management('课程进度人员')
            self.page.get_by_role('button', name='图标: plus 批量新增').click()
            self.page.get_by_placeholder('请选择').click()
            self.page.get_by_placeholder('请输入课程编码').fill(course_code)
            self.page.get_by_placeholder('请输入课程进度').fill(
                the_progress_of_the_curriculum
            )
            self.page.get_by_role('button', name='图标: search 查询').click()
            self.page.get_by_label('课程进度').get_by_role(
                'cell', name=course_code
            ).click()
            self.page.get_by_label('课程进度').get_by_role(
                'button', name='确 定'
            ).click()
            self.page.get_by_role('button', name='确 定').click()
            self.page.wait_for_load_state('networkidle')
            logger.info(
                f'{course_code}-{the_progress_of_the_curriculum} 班级人员添加成功'
            )
        except PWTimeout:
            raise BizError(
                f'{course_code}-{the_progress_of_the_curriculum} 班级人员添加失败'
            )

    @validate_call
    def add_schedule(
        self,
        course_code: str,
        the_progress_of_the_curriculum: str,
        begin_time: int,
        end_time: int,
        course_state: ALLOWED_COURSE_STATE,
        course_content: str,
    ) -> None:
        """一键添加班级"""
        self.add_progress(
            course_code,
            the_progress_of_the_curriculum,
            begin_time,
            end_time,
            course_state,
            course_content,
        )
        self.add_members(
            course_code,
            the_progress_of_the_curriculum,
        )

    ALLOWED_USER_STATE = Literal[
        '请选择',
        '无效',
        '完成课程',
        '请假',
        '请假已补课',
    ]

    @validate_call
    def set_user_state(
        self,
        course_code: str,
        the_progress_of_the_curriculum: str,
        user_name: str,
        state: ALLOWED_USER_STATE,
    ) -> None:
        """设置用户状态"""
        try:
            self.to_management('课程进度人员')

            # 查找当前班的人
            self.page.get_by_role('button', name='图标: filter 高级查询').click()

            self.page.wait_for_timeout(1000)
            self.page.locator('div').filter(
                has_text=re.compile(r'^选择查询字段$')
            ).locator('svg').click()

            self.page.get_by_title('进度id').click()
            self.page.get_by_placeholder('请选择').click()
            self.page.get_by_placeholder('请输入课程编码').fill(course_code)
            self.page.get_by_placeholder('请输入课程进度').fill(
                the_progress_of_the_curriculum
            )

            self.page.get_by_role('button', name='图标: search 查询').click()
            self.page.get_by_label('课程进度').get_by_role(
                'cell', name=course_code
            ).click()
            self.page.get_by_role('button', name='确 定').click()

            self.page.get_by_role(
                'button',
                name='图标: plus',
                exact=True,
            ).click()
            self.page.locator('div').filter(
                has_text=re.compile(r'^选择查询字段$')
            ).locator('svg').click()

            self.page.locator('#rc-tree-select-list_2').get_by_text('用户id').click()
            self.page.get_by_label('高级查询构造器').locator('form div').filter(
                has_text='用户id 用户id成员类型进度id上课状态创建时间匹配规则等于'
            ).get_by_placeholder('请选择').click()
            self.page.get_by_placeholder('请输入用户名字').fill(user_name)
            self.page.get_by_role('button', name='图标: search 查询').click()
            self.page.get_by_label('成员查询').get_by_role(
                'cell', name=user_name
            ).click()
            self.page.get_by_role('button', name='确 定').click()

            self.page.get_by_role('button', name='查 询').click()
            self.page.get_by_role('button', name='Close').click()

            self.page.get_by_text('编辑').nth(1).click()

            self.page.wait_for_timeout(1000)
            self.page.get_by_role('combobox').filter(has_text='请选择上课状态').click()
            self.page.get_by_role('option', name=state, exact=True).locator(
                'span'
            ).click()
            self.page.get_by_role('button', name='确 定').click()
            self.page.wait_for_load_state('networkidle')
            logger.info(
                f'{course_code}-{the_progress_of_the_curriculum}-{user_name} 班级状态设置为{state}'
            )
        except PWTimeout:
            raise BizError(
                f'{course_code}-{the_progress_of_the_curriculum}-{user_name} 班级状态设置失败'
            )

    # 增加已经完成的学生
    def set_users_over(
        self,
        course_code: str,
        the_progress_of_the_curriculum: str,
        user_names: list[str],
    ) -> None:
        for user_name in user_names:
            self.set_user_state(
                course_code,
                the_progress_of_the_curriculum,
                user_name,
                '完成课程',
            )

    # 增加请假的学生
    def set_users_leave(
        self,
        course_code: str,
        the_progress_of_the_curriculum: str,
        user_names: list[str],
    ) -> None:
        for user_name in user_names:
            self.set_user_state(
                course_code,
                the_progress_of_the_curriculum,
                user_name,
                '请假',
            )

    def add_discuss(
        self,
        course_code: str,
        the_progress_of_the_curriculum: str,
    ) -> None:
        """批量增加班级人员课评"""
        try:
            self.to_management('课后反馈中心')
            self.page.get_by_role('button', name='图标: plus 批量新增').click()
            self.page.get_by_placeholder('请选择').click()
            self.page.get_by_placeholder('请输入课程编码').fill(course_code)
            self.page.get_by_placeholder('请输入课程进度').fill(
                the_progress_of_the_curriculum
            )
            self.page.get_by_role('button', name='图标: search 查询').click()

            self.page.get_by_label('课程进度').get_by_role(
                'cell', name=course_code
            ).click()
            self.page.get_by_label('课程进度').get_by_role(
                'button', name='确 定'
            ).click()
            self.page.get_by_role('button', name='确 定').click()
            self.page.wait_for_load_state('networkidle')
            logger.info(
                f'{course_code}-{the_progress_of_the_curriculum} 班级人员课评添加成功'
            )
        except PWTimeout:
            raise BizError(
                f'{course_code}-{the_progress_of_the_curriculum} 班级人员课评添加失败'
            )

    ALLOWED_DISCUSS_STATE = Literal[
        '请选择',
        '审核中（未发送）',
        '无效',
    ]

    @validate_call
    def set_user_state_discuss(
        self,
        course_code: str,
        the_progress_of_the_curriculum: str,
        course_content: str,
        discuss_content: str,
        user_name: str,
        state: ALLOWED_DISCUSS_STATE,
    ) -> None:
        """设置人员课评状态"""
        try:
            self.to_management('课后反馈中心')

            # 查找当前班的人
            self.page.get_by_role('button', name='图标: filter 高级查询').click()

            self.page.locator('div').filter(
                has_text=re.compile(r'^选择查询字段$')
            ).locator('svg').click()

            self.page.get_by_title('进度id').click()
            self.page.get_by_placeholder('请选择').click()
            self.page.get_by_placeholder('请输入课程编码').fill(course_code)
            self.page.get_by_placeholder('请输入课程进度').fill(
                the_progress_of_the_curriculum
            )

            self.page.get_by_role('button', name='图标: search 查询').click()
            self.page.get_by_label('课程进度').get_by_role(
                'cell', name=course_code
            ).click()
            self.page.get_by_role('button', name='确 定').click()

            self.page.get_by_role(
                'button',
                name='图标: plus',
                exact=True,
            ).click()
            self.page.locator('div').filter(
                has_text=re.compile(r'^选择查询字段$')
            ).locator('svg').click()

            self.page.locator('#rc-tree-select-list_2').get_by_text('人员名称').click()
            self.page.get_by_label('高级查询构造器').locator('form div').filter(
                has_text='人员名称 课后评价进度id状态人员名称标题课堂表现等级创建时间匹配规则等于'
            ).get_by_placeholder('请选择').click()
            self.page.get_by_placeholder('请输入用户名字').fill(user_name)
            self.page.get_by_role('button', name='图标: search 查询').click()
            self.page.get_by_label('成员查询').get_by_role(
                'cell', name=user_name
            ).click()
            self.page.get_by_role('button', name='确 定').click()

            self.page.get_by_role('button', name='查 询').click()
            self.page.get_by_role('button', name='Close').click()

            self.page.get_by_text('编辑').nth(1).click()

            self.page.get_by_role('textbox', name='请输入课后评价').fill(
                discuss_content
            )

            self.page.get_by_role('combobox').filter(has_text='请选择状态').click()

            self.page.get_by_role('option', name=state, exact=True).locator(
                'span'
            ).click()

            self.page.get_by_role('textbox', name='请输入标题').fill(course_content)

            self.page.get_by_role('button', name='确 定').click()
            self.page.wait_for_load_state('networkidle')
            logger.info(
                f'{course_code}-{the_progress_of_the_curriculum}-{user_name} 课评状态设置{state}'
            )
        except PWTimeout:
            raise BizError(
                f'{course_code}-{the_progress_of_the_curriculum}-{user_name} 课评状态设置失败'
            )

    @validate_call
    def set_user_state_discusses(
        self,
        course_code: str,
        the_progress_of_the_curriculum: str,
        course_content: str,
        discuss_contents: list[str],
        user_names: list[str],
        state: ALLOWED_DISCUSS_STATE,
    ) -> None:
        if len(user_names) != len(discuss_contents):
            raise ValueError('用户和课评对不上')

        for user_name, discuss_content in zip(user_names, discuss_contents):
            self.set_user_state_discuss(
                course_code,
                the_progress_of_the_curriculum,
                course_content,
                discuss_content,
                user_name,
                state,
            )
