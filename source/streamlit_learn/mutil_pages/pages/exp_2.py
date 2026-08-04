import streamlit as st
st.title("网页分栏 1")
with st.sidebar:
    name = st.text_input("请输入你的名字：")
    if name:
        st.write(f"你好，{name}")
st.write("### 划分 3 个分栏")
col1, col2, col3 = st.columns(3) # 均匀划分
with col1:
    password = st.text_input("请输入你的密码：", type="password")
with col2:
    paragraph = st.text_area("请输入一段自我介绍：")
with col3:
    age = st.number_input("请输入你的年龄：", value=20, min_value=0, max_value=150, step=1)
    st.write(f"你的年龄是：{age}岁")

st.divider()
checked = st.checkbox("我同意以上条款")
if checked:
    st.write("感谢你的同意！")

st.divider()
col1, col2, col3 = st.columns([1,3,1]) # 非均匀划分
with col1:
    password = st.text_input("请输入你的密码：", type="password", key="password2")
with col2:
    paragraph = st.text_area("请输入一段自我介绍：", key="paragraph2")
with col3:
    age = st.number_input("请输入你的年龄：", value=20, min_value=0, max_value=150, step=1, key="age2")
    st.write(f"你的年龄是：{age}岁")
# 上面加 key 参数是为了避免和上面重复的组件冲突，key 参数可以理解为组件的唯一标识符.

# 交互式组件是 Streamlit 中所有能接收用户操作和输入的界面元素，比如输入框、按钮、复选框、滑块等。
# 这些组件不仅仅是显示在页面上的控件，它们还承担着保存用户输入状态的功能，
# 而Streamlit正是通过每个组件独有的“key”值来区分和追踪不同组件的状态。


st.divider()
submitted = st.button("提交")
if submitted:
    st.write("提交成功！")

st.divider()
st.title("网页分栏 2: 选项卡式导航容器")
# st.tabs() 形成的是一个选项卡式导航容器，它会在您的网页上创建一组水平排列的
# 标签页标题，每个标题对应一个独立的内容面板。当用户点击不同的标签标题时，
# 页面会切换显示对应面板中的内容，而其他面板的内容则会被隐藏起来
tab1, tab2, tab3 = st.tabs(["性别", "联系方式", "喜好水果"])
with tab1:
    gender = st.radio("你的性别是什么？", ["男性", "女性", "跨性别"], index=None)
    if gender:
        st.write(f"你选择的性别是{gender}")

with tab2:
    contact = st.selectbox("你希望通过什么方式联系？",
                 ["电话", "邮件", "微信", "QQ", "其它"])
    st.write(f"好的，我们会通过{contact}联系你")

with tab3:
    fruits = st.multiselect("你喜欢的水果是什么？",
                   ["苹果", "香蕉", "橙子", "梨", "西瓜", "葡萄", "其它"])
    for fruit in fruits:
        st.write(f"你选择的水果是{fruit}")

st.divider()
st.write("### 隐藏块")
with st.expander("身高信息"):
    height = st.slider("你的身高是多少厘米？", value=170, min_value=100, max_value=230, step=1)
    st.write(f"你的身高是{height}厘米")

st.divider()
uploaded_file = st.file_uploader("上传文件", type=["py"])
if uploaded_file:
    st.write(f"你上传的文件是{uploaded_file.name}")
    st.write(f"文件内容是{uploaded_file.read()}")