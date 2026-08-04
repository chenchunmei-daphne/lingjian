import streamlit as st

"st.session_state 是 Streamlit 中一个极为重要的状态管理字典对象，\
它允许您在用户与应用程序交互的过程中，跨多次页面运行和重新渲染来持久化保存和访问数据。"

if "number" not in st.session_state:
    st.session_state.number = 0
clicked = st.button("加1")
if clicked:
    st.session_state.number +=1
st.write(st.session_state.number)
print(st.session_state) # 终端输出
