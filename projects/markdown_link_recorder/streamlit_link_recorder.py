from __future__ import annotations

from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st


# =========================
# 配置
# =========================

# 修改为实际需要写入的 Markdown 文件路径。
TARGET_MARKDOWN_FILE = Path(
    r"D:\chen\repo\web_links.md"
)

# 日期标题格式，例如：## 8月4日
DATE_HEADING_FORMAT = "%-m月%-d日"


# =========================
# 工具函数
# =========================

def get_date_heading(now: datetime) -> str:
    """生成日期分组标题，兼容 Windows 和 Linux/macOS。"""
    try:
        return now.strftime(DATE_HEADING_FORMAT)
    except ValueError:
        # Windows 不支持 %-m 和 %-d。
        return f"{now.month}月{now.day}日"


def is_valid_url(url: str) -> bool:
    """仅允许 http 或 https URL。"""
    try:
        parsed = urlparse(url.strip())
    except ValueError:
        return False

    return (
        parsed.scheme in {"http", "https"}
        and bool(parsed.netloc)
    )


def escape_markdown_link_text(text: str) -> str:
    """转义 Markdown 链接文本中的特殊字符。"""
    return (
        text.replace("\\", "\\\\")
        .replace("[", r"\[")
        .replace("]", r"\]")
    )


def normalize_markdown_content(content: str) -> str:
    """统一文件尾部换行，避免追加内容粘连。"""
    return content.rstrip() + "\n"


def append_link_to_markdown(
    file_path: Path,
    link_text: str,
    url: str,
    now: datetime | None = None,
) -> str:
    """
    将链接按日期分组追加到 Markdown 文件末尾。

    返回实际写入的 Markdown 链接。
    """
    now = now or datetime.now()
    date_heading = f"## {get_date_heading(now)}"
    safe_text = escape_markdown_link_text(link_text.strip())
    clean_url = url.strip()
    markdown_link = f"[{safe_text}]({clean_url})"

    file_path.parent.mkdir(parents=True, exist_ok=True)

    if file_path.exists():
        content = file_path.read_text(encoding="utf-8")
    else:
        content = ""

    normalized = normalize_markdown_content(content) if content.strip() else ""

    # 采用按时间顺序追加的写法：
    # 当文件末尾当前分组就是今天时，仅追加链接；
    # 否则在末尾创建新的日期分组。
    lines = normalized.rstrip().splitlines() if normalized else []
    last_date_heading = next(
        (line.strip() for line in reversed(lines) if line.startswith("## ")),
        None,
    )

    if last_date_heading == date_heading:
        new_content = normalized + f"{markdown_link}\n"
    else:
        separator = "\n" if normalized else ""
        new_content = (
            normalized
            + separator
            + f"{date_heading}\n\n"
            + f"{markdown_link}\n"
        )

    # 先写入临时文件，再替换目标文件，降低写入中断导致文件损坏的风险。
    temp_file = file_path.with_suffix(file_path.suffix + ".tmp")
    temp_file.write_text(new_content, encoding="utf-8")
    temp_file.replace(file_path)

    return markdown_link


# =========================
# Streamlit 页面
# =========================

st.set_page_config(
    page_title="网页链接记录工具",
    page_icon="🔗",
    layout="centered",
)

st.title("网页链接记录工具")
st.write("输入网页标识信息和网页地址，提交后自动写入指定的 Markdown 文件。")

st.info(f"当前写入文件：`{TARGET_MARKDOWN_FILE}`")

with st.form("link_form", clear_on_submit=True):
    link_text = st.text_input(
        "网页标识信息",
        placeholder="例如：信道开源数据查找",
        max_chars=200,
    )

    url = st.text_input(
        "网页地址",
        placeholder="例如：https://chatgpt.com/...",
    )

    submitted = st.form_submit_button(
        "写入 Markdown",
        type="primary",
        use_container_width=True,
    )

if submitted:
    clean_text = link_text.strip()
    clean_url = url.strip()

    if not clean_text:
        st.error("网页标识信息不能为空。")
    elif "\n" in clean_text or "\r" in clean_text:
        st.error("网页标识信息不能包含换行。")
    elif not clean_url:
        st.error("网页地址不能为空。")
    elif not is_valid_url(clean_url):
        st.error("网页地址必须是有效的 http 或 https URL。")
    else:
        try:
            written_link = append_link_to_markdown(
                file_path=TARGET_MARKDOWN_FILE,
                link_text=clean_text,
                url=clean_url,
            )
        except PermissionError:
            st.error(
                "没有写入权限。请检查目标文件是否被其他程序占用，"
                "以及当前用户是否具有该目录的写入权限。"
            )
        except OSError as exc:
            st.error(f"写入失败：{exc}")
        else:
            st.success("写入成功。")
            st.code(written_link, language="markdown")


with st.expander("查看写入规则"):
    st.markdown(
        """
- 同一天提交的链接放在同一个 `## x月x日` 标题下。
- 新的一天首次提交时，在文件末尾创建新的日期标题。
- 每次点击提交按钮只写入一条记录。
- 链接采用 `[网页标识信息](网页地址)` 格式。
"""
    )
