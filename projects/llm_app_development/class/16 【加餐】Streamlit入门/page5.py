import streamlit as st

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

with st.expander("身高信息"):
    height = st.slider("你的身高是多少厘米？", value=170, min_value=100, max_value=230, step=1)
    st.write(f"你的身高是{height}厘米")

st.divider()
uploaded_file = st.file_uploader("上传文件", type=["py"])
if uploaded_file:
    st.write(f"你上传的文件是{uploaded_file.name}")
    st.write(f"文件内容是{uploaded_file.read()}")
