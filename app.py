import streamlit as st
from llm_client import LLMClient
from prompts import CODE_COMMENT_SYSTEM, build_comment_prompt
if "count" not in st.session_state:
    st.session_state.count = 0

st.set_page_config(page_title="AI代码注释生成器", page_icon="🤖")
st.title("🤖 AI代码注释生成器")
st.write(f"生成次数：{st.session_state.count}")
if "history" not in st.session_state:
    st.session_state.history = []
with st.sidebar:
    st.header("📜 生成历史")
    if len(st.session_state.history) == 0:
        st.info("暂无历史记录")
    else:
        for i, item in enumerate(st.session_state.history):
            with st.expander(f"记录 {i+1} ({item['language']})"):
                st.code(item["code"], language="python")
                st.caption("生成的注释：")
                st.text(item["comment"][:100] + "..." if len(item["comment"]) > 100 else item["comment"])


api_key = st.text_input("请输入你的API Key", type="password")
code_input = st.text_area("粘贴你的代码", height=300)
language = st.selectbox("选择语言", ["Python", "Java"])
temperature = st.slider("创意程度", min_value=0.0, max_value=1.0, value=0.3, step=0.1)

if st.button("生成注释"):
    if not api_key:
        st.error("请输入API Key")
    elif not code_input:
        st.error("请输入代码")
    else:
        st.session_state.count += 1
        client = LLMClient(api_key)
        user_message = build_comment_prompt(code_input, language)

        # 流式输出
        result_placeholder = st.empty()  # 占个位置
        full_result = ""


        for chunk in client.chat_stream(user_message, system_message=CODE_COMMENT_SYSTEM, temperature=temperature):
            full_result += chunk
            result_placeholder.code(full_result + "▌", language="python")  # 显示一个光标
        st.session_state.history.append({
            "code": code_input,
            "comment": full_result,
            "language": language
        })


        # 最后显示完整结果（去掉光标）
        result_placeholder.code(full_result, language="python")