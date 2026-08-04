# streamlit hello 在终端测试是否安装成功，成功会打开一个网页，终止运行：ctrl+C

import streamlit as st

# 运行 streamlit run exp_1.py
st.title("First class of streamlit")
st.write("## Hello, Streamlit! ")  # write() 函数的内容支持 markdown 的语法

"### input text"
a = 100**2
a
[11,90, 33]
{"a":1, "b":"a"}

"### input image"
st.image("D:/chen/repo/xuantong/kb/projects/wireless_channel/knowledge/wireless_channel_simulation/antenna/天线.png", width=400, caption="This is a image about anntena")

"### input dataframe"
import pandas as pd
df = pd.DataFrame({"姓名": ["张三", "李四", "apple"],
                   "年龄": [18, 19, 20],
              "成绩": [92, 67, 85]})
st.dataframe(df) # 可互动的表格
st.divider() # 分割线
st.table(df) # 静态表格

st.divider()
st.title("Second class of streamlit")
name = st.text_input("Please input your name:")
if name:
    st.write(f"How are you, my dear friend {name}?")
# 网页什么时候进行更行：文件被更改或者用户输入数据时网页

st.divider()
password = st.text_input("Please input your password:", type='password')

st.divider()
selfintroduction = st.text_area("Please input a self-introduction:")

st.divider()
age = st.number_input("Please input your age:", value=1, step=1, min_value=0, max_value=120) # 参数的类型要统一为 float 或者 int，否则报错

st.divider()
checked = st.checkbox("I agree the above terms")
if checked:
    st.write("Thanks for your agreement!")

st.divider()
submitted = st.button("提交")
if submitted:
    st.write("提交成功！")

st.divider()
st.title("Third class of streamlit")
st.write("### 单选题")

gender = st.radio("What os your gender?", ["女性","男性", "其他"], index=None) # index 提供默认选项，None为没有默认选项
if gender:
    st.write(f"你选择的性别是：{gender}.")

contact = st.selectbox("What is your contact way?", ["电话","邮件","微信", "QQ", "其他"], index=None)
st.write(f"好的，我们会通过{contact}联系你。")

st.divider()
st.write("### 多选题")
fruits = st.multiselect("What is your favorite fruit?", ["苹果","香蕉","橙子","梨","西瓜","葡萄", "其他"])
if fruits:
    st.write(f"你选择的水果是：{', '.join(fruits)}.")

st.divider()
st.write("### 滑动条")
height = st.slider("What is your height?", value=170, min_value=100, max_value=230, step=1)
st.write(f"你的身高是：{height}厘米.")

st.divider()
st.write("### 上传文件")
uploaded_file = st.file_uploader("上传文件", type=["py"])
if uploaded_file:
    st.write(f"你上传的文件是：{uploaded_file.name}.")
    st.write(f"文件内容如下：{uploaded_file.read()}.")






