# Markdown Link Recorder

Markdown Link Recorder 是一个基于 Streamlit 构建的轻量级网页工具，用于将网页标识信息和网页地址按日期追加写入指定的 Markdown 文件。

## 功能

* 输入网页标识信息和网页地址
* 自动生成 Markdown 链接
* 按日期对链接进行分组
* 按提交顺序追加记录
* 自动创建目标文件和父目录
* 校验网页地址是否合法
* 显示写入成功或失败信息

写入格式示例：

```markdown
## 8月4日

[信道开源数据查找](https://chatgpt.com/example)
```

## 项目结构

```text
markdown_link_recorder/
├── streamlit_link_recorder.py
└── README.md
```

目前项目仅包含一个程序文件：

* `streamlit_link_recorder.py`：Streamlit 网页应用主程序

## 环境要求

* Python 3.8 及以上版本
* Streamlit

安装依赖：

```bash
pip install streamlit
```

## 配置

打开 `streamlit_link_recorder.py`，修改目标 Markdown 文件路径：

```python
TARGET_MARKDOWN_FILE = Path(
    r"D:\chen\repo\xuantong\kb\web_links.md"
)
```

## 运行

在项目目录下执行：

```bash
streamlit run streamlit_link_recorder.py
```

运行后，浏览器通常会自动打开：

```text
http://localhost:8501
```

停止程序：

```text
Ctrl + C
```

## 使用说明

1. 输入网页标识信息。
2. 输入完整的网页地址。
3. 点击“写入 Markdown”。
4. 程序会将链接写入指定 Markdown 文件。
5. 同一天提交的链接会归入同一个日期标题下。

## 当前状态

当前版本为最小可用版本，仅包含单文件 Streamlit 应用，适用于个人日常记录网页链接。
