# Streamlit 学习笔记

## 一、什么是 Streamlit

Streamlit 是一个用于快速构建 Python Web 应用的轻量级框架，特别适合数据分析、机器学习模型展示和算法 Demo。整个页面由 Python 脚本直接生成，无需编写 HTML、CSS 或 JavaScript。以上内容均根据三个示例程序（[程序 1](./exp_1.py)、[程序 2](./exp_2.py)、[程序 3](./exp_3.py)）总结。

## 二、运行程序
安装：

```bash
pin install streamlit 
```

安装测试：

```bash
streamlit hello
```

运行应用：

```bash
streamlit run exp_1.py
```

停止运行：

```text
Ctrl + C
```

> **注意：** 页面会在脚本修改或用户交互时自动重新执行脚本。

## 三、页面输出

### 标题

```python
st.title("标题")
```

### Markdown

```python
st.write("## Hello")
```

### 图片

```python
st.image(path, width=400, caption="说明")
```

### 表格

```python
st.dataframe(df)
st.table(df)
```

其中：

- `dataframe`：可交互。
- `table`：静态显示。

### 分隔线

```python
st.divider()
```

## 四、输入组件

常见输入组件如下。

|组件|函数|
|---|---|
|单行文本|`st.text_input()`|
|密码|`type="password"`|
|多行文本|`st.text_area()`|
|数字输入|`st.number_input()`|
|按钮|`st.button()`|
|复选框|`st.checkbox()`|
|文件上传|`st.file_uploader()`|

> **注意：** `number_input()` 的默认值、最小值、最大值类型必须保持一致。

## 五、选择组件

### 单选

```python
st.radio(...)
```

### 下拉框

```python
st.selectbox(...)
```

### 多选

```python
st.multiselect(...)
```

### 滑块

```python
st.slider(...)
```

## 六、页面布局

### Sidebar

```python
with st.sidebar:
    ...
```

### Columns

```python
st.columns(3)
st.columns([1,3,1])
```

### Tabs

```python
st.tabs([...])
```

### Expander

```python
with st.expander(...):
    ...
```

以上布局方式均来自 `exp_2.py`。fileciteturn0file1

## 七、组件 key

重复创建同类型组件时，需要指定不同的 `key`。

```python
st.text_input(..., key="password2")
```

`key` 可以理解为组件唯一标识，用于区分不同组件并保存状态。fileciteturn0file1

## 八、Session State

`st.session_state` 用于跨页面刷新保存变量。

初始化：

```python
if "number" not in st.session_state:
    st.session_state.number = 0
```

修改：

```python
st.session_state.number += 1
```

读取：

```python
st.write(st.session_state.number)
```

这是 Streamlit 最重要的状态管理机制之一。fileciteturn0file2

## 九、页面刷新机制

页面重新执行主要发生在：

- 修改 Python 文件；
- 用户输入；
- 点击按钮；
- 修改滑块；
- 选择单选、多选等。

重新执行后，普通变量重新初始化，而 `st.session_state` 中的数据仍会保留。 fileciteturn0file2

## 十、典型开发流程

1. 使用 `st.title()`、`st.write()` 搭建页面。
2. 添加输入组件。
3. 根据输入编写业务逻辑。
4. 使用布局优化页面。
5. 使用 `session_state` 保存状态。

## 十一、学习建议

建议学习顺序：

1. 页面输出。
2. 输入组件。
3. 选择组件。
4. 页面布局。
5. 状态管理。
6. 完整 Demo 开发。

根据三个实验文件，已经基本覆盖了 Streamlit 的基础使用流程，能够完成简单 Web 工具的开发。
