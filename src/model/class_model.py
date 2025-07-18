from pydantic import BaseModel, Field


class CourseModel(BaseModel):
    code: str = Field(..., description='课程编号')
    progress: str = Field(..., description='课程进度')
    content: str = Field(..., description='课程内容')
    time: tuple[int, int] = Field(..., description='(开始小时, 结束小时)')
    state: str = Field('已结束', description='课程状态')
    discuss_state: str = Field('无效', description='课评状态')
    users_over: list[str] = Field(default_factory=list, description='正常上课的学生')
    users_leave: list[str] = Field(default_factory=list, description='请假的学生')
    discuss_content: list[str] = Field(default_factory=list, description='课评内容')

    class Config:
        # 支持 json.dumps(c.model_dump(), ensure_ascii=False)
        json_encoders = {tuple[int, int]: lambda t: list(t)}
