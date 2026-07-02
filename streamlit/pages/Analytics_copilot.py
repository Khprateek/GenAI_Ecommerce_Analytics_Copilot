import streamlit as st

st.set_page_config(
    page_title="Analytics Copilot",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Analytics Copilot")
st.caption(
    "Ask questions about your e-commerce business using natural language."
)

# -----------------------------
# Session State
# -----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I'm your Analytics Copilot.\n\n"
                "Currently I'm running in Chat Mode.\n\n"
                "Soon I'll be able to generate SQL, query BigQuery, "
                "build charts and explain business trends."
            ),
        }
    ]


# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:

    st.header("Analytics Copilot")

    st.write("Example Questions")

    st.button("📈 Show revenue by category")
    st.button("🏆 Top selling products")
    st.button("📣 Marketing ROI")
    st.button("👥 Customer segments")

    st.divider()

    if st.button("🗑 Clear Conversation"):

        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Conversation cleared. How can I help you today?"
            }
        ]

        st.rerun()


# -----------------------------
# Chat History
# -----------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -----------------------------
# User Input
# -----------------------------

prompt = st.chat_input(
    "Ask a business question..."
)

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # Temporary response (Phase 1)

    response = f"""
You asked:

> **{prompt}**

I'm currently operating in **Chat Mode**.

In the next phase I'll:

- Understand your business question
- Generate SQL
- Query BigQuery
- Create charts
- Explain the results

Stay tuned!
"""

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )

    with st.chat_message("assistant"):
        st.markdown(response)