import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any
import ddddocr
from playwright.sync_api import Locator, Page

_ocr = ddddocr.DdddOcr(show_ad=False)


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


def highlight_element(
    page: Page,
    locator: Locator,
    color: str = 'red',
    width: int = 2,
) -> Callable[[], None]:
    """
    在元素周围添加高亮边框，返回移除函数。
    """
    box = locator.bounding_box()
    if not box:
        raise RuntimeError('元素未找到或不可见')

    element_id = f'playwright-highlight-{uuid.uuid4()}'

    js = f"""
    const box = {box};
    const div = document.createElement('div');
    div.id = '{element_id}';
    div.style.position = 'absolute';
    div.style.left   = box.x + 'px';
    div.style.top    = box.y + 'px';
    div.style.width  = box.width + 'px';
    div.style.height = box.height + 'px';
    div.style.border = '{width}px solid {color}';
    div.style.pointerEvents = 'none';
    div.style.zIndex = '9999';
    document.body.appendChild(div);
    """
    page.evaluate(js)

    def remove() -> None:
        page.evaluate(f"document.getElementById('{element_id}')?.remove()")

    return remove


def highlight_action(page, action, *args, **kwargs) -> Any | Callable[[], None]:
    """
    original_click = page.click
    page.click = lambda *args, **kwargs: highlight_action(
        page, original_click, *args, **kwargs
    )

    original_fill = page.fill
    page.fill = lambda *args, **kwargs: highlight_action(
        page, original_fill, *args, **kwargs
    )
    """
    selector = kwargs.get('selector') or (args[0] if args else None)
    if not selector:
        return action(*args, **kwargs)

    locator = page.locator(selector)
    if locator.count() == 0:
        return action(*args, **kwargs)

    box = locator.bounding_box()
    if not box:
        return action(*args, **kwargs)

    highlight_id = f'highlight-{uuid.uuid4()}'

    js = f"""
    (function() {{
        const target = document.querySelector('{selector}');
        if (!target) return;

        const div = document.createElement('div');
        div.id = '{highlight_id}';
        div.style.position = 'absolute';
        div.style.border = '2px solid red';
        div.style.zIndex = '9999';
        div.style.pointerEvents = 'none';
        document.body.appendChild(div);

        function updatePosition() {{
            const box = target.getBoundingClientRect();
            div.style.left = `${{box.x + window.scrollX}}px`;
            div.style.top = `${{box.y + window.scrollY}}px`;
            div.style.width = `${{box.width}}px`;
            div.style.height = `${{box.height}}px`;
        }}

        const observer = new MutationObserver(updatePosition);
        observer.observe(target, {{
            attributes: true,
            childList: true,
            subtree: true
        }});

        window.addEventListener('scroll', updatePosition);
        window.addEventListener('resize', updatePosition);

        updatePosition();

        window.cleanupHighlight = () => {{
            observer.disconnect();
            window.removeEventListener('scroll', updatePosition);
            window.removeEventListener('resize', updatePosition);
            div.remove();
        }};
    }})();
    """
    page.evaluate(js)

    result = action(*args, **kwargs)

    def cleanup():
        page.evaluate('window.cleanupHighlight()')

    return cleanup


def install_auto_highlight(page: Page) -> None:
    """安装自动高亮系统（覆盖所有 locator 操作）"""
    original_locator = page.locator

    def highlighting_locator(selector: str, *args, **kwargs) -> Locator:
        locator = original_locator(selector, *args, **kwargs)
        _highlight_element(page, selector)
        return locator

    page.locator = highlighting_locator


def _highlight_element(page: Page, selector: str) -> None:
    """为元素添加高亮边框"""
    highlight_id = f'highlight-{uuid.uuid4()}'

    js = f"""
    (function() {{
        const elements = document.querySelectorAll('{selector}');
        if (elements.length === 0) return;

        // 为每个匹配元素创建高亮框
        elements.forEach(element => {{
            const div = document.createElement('div');
            div.id = '{highlight_id}-' + Math.random().toString(36).slice(2);
            div.style.position = 'absolute';
            div.style.border = '2px solid red';
            div.style.zIndex = '99999';
            div.style.pointerEvents = 'none';
            document.body.appendChild(div);

            function updatePosition() {{
                const box = element.getBoundingClientRect();
                div.style.left = `${{box.x + window.scrollX}}px`;
                div.style.top = `${{box.y + window.scrollY}}px`;
                div.style.width = `${{box.width}}px`;
                div.style.height = `${{box.height}}px`;
            }}

            const observer = new MutationObserver(updatePosition);
            observer.observe(element, {{
                attributes: true,
                childList: true,
                subtree: true
            }});

            window.addEventListener('scroll', updatePosition);
            window.addEventListener('resize', updatePosition);
            updatePosition();

            // 存储清理函数
            window.__playwright_highlights = window.__playwright_highlights || {{}};
            window.__playwright_highlights[div.id] = () => {{
                observer.disconnect();
                window.removeEventListener('scroll', updatePosition);
                window.removeEventListener('resize', updatePosition);
                div.remove();
            }};
        }});
    }})();
    """
    page.evaluate(js)


def clear_all_highlights(page: Page) -> None:
    """清除所有高亮框"""
    page.evaluate("""
    (function() {
        if (!window.__playwright_highlights) return;
        Object.values(window.__playwright_highlights).forEach(cleanup => cleanup());
    })();
    """)
