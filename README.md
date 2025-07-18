# 自动化课程评价系统

一个基于Python的自动化Web应用，用于课程评价管理

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 功能特性

### 核心功能
- 课程管理
  - 课程列表查看与搜索
  - 课程评价提交
  - 评价结果统计与分析
- 用户系统
  - 安全的登录认证
  - 权限管理
  - 用户行为日志

### 技术特性
- 基于Playwright的浏览器自动化
- 可配置的运行参数
  - 支持无头模式
  - 自定义视窗大小
  - 多语言支持
- 模块化设计
  - 易于扩展新功能
  - 清晰的代码结构

## 安装指南

1. 克隆仓库：
   ```bash
   git clone [仓库URL]
   cd [项目目录]
   ```

2. 创建虚拟环境：
   ```bash
   python -m venv .venv
   ```

3. 激活虚拟环境：
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - Mac/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. 安装依赖：
   ```bash
   pip install -e .
   ```

## 配置说明

1. 复制配置文件模板：
   ```bash
   cp config.example.toml config.toml
   ```

2. 编辑config.toml文件：
   - 设置base_url为你的系统地址
   - 填写用户名和密码凭证
   - 配置浏览器参数

3.编写 coures.json文件

## 运行项目

```bash
python src/main.py
```
