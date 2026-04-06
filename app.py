import streamlit as st
from llm_client import LLMClient
from prompts import CODE_COMMENT_SYSTEM, build_comment_prompt

# ========== 页面配置 ==========
st.set_page_config(page_title="AI代码注释生成器", page_icon="🤖")


# ========== 初始化 session_state ==========
def init_session_state():
    """初始化所有 session_state 变量"""
    if "count" not in st.session_state:
        st.session_state.count = 0
    if "history" not in st.session_state:
        st.session_state.history = []


init_session_state()


# ========== 侧边栏（历史记录） ==========
def render_sidebar():
    """渲染侧边栏历史记录"""
    with st.sidebar:
        st.header("📜 生成历史")
        if len(st.session_state.history) == 0:
            st.info("暂无历史记录")
        else:
            for i, item in enumerate(st.session_state.history):
                with st.expander(f"记录 {i + 1} ({item['language']})"):
                    st.code(item["code"], language="python")
                    st.caption("生成的注释：")
                    preview = item["comment"][:100] + "..." if len(item["comment"]) > 100 else item["comment"]
                    st.text(preview)


# ========== 主界面 ==========
def render_main():
    """渲染主界面"""
    st.title("🤖 AI代码注释生成器")
    st.write(f"生成次数：{st.session_state.count}")


# ========== 输入区域 ==========
def render_inputs():
    """渲染输入控件"""
    api_key = st.text_input("请输入你的API Key", type="password")
    code_input = st.text_area("粘贴你的代码", height=300)

    col1, col2 = st.columns(2)  # 两列布局，更紧凑
    with col1:
        language = st.selectbox("选择语言", ["Python", "Java"])
    with col2:
        temperature = st.slider("创意程度", min_value=0.0, max_value=1.0, value=0.3, step=0.1)

    return api_key, code_input, language, temperature


# ========== 生成注释逻辑 ==========
def generate_comment(api_key, code_input, language, temperature):
    """调用 API 生成注释并更新状态"""
    # 更新计数
    st.session_state.count += 1

    # 调用 API
    client = LLMClient(api_key)
    user_message = build_comment_prompt(code_input, language)

    # 流式输出占位符
    result_placeholder = st.empty()
    full_result = ""

    # 流式接收
    for chunk in client.chat_stream(user_message, system_message=CODE_COMMENT_SYSTEM, temperature=temperature):
        full_result += chunk
        result_placeholder.code(full_result + "▌", language="python")

    # 保存历史
    st.session_state.history.append({
        "code": code_input,
        "comment": full_result,
        "language": language
    })

    # 最终显示（去掉光标）
    result_placeholder.code(full_result, language="python")


# ========== 主流程 ==========
def main():
    render_sidebar()
    render_main()
    api_key, code_input, language, temperature = render_inputs()

    if st.button("生成注释", type="primary"):  # type="primary" 让按钮更醒目
        if not api_key:
            st.error("请输入API Key")
        elif not code_input:
            st.error("请输入代码")
        else:
            generate_comment(api_key, code_input, language, temperature)


if __name__ == "__main__":
    main()