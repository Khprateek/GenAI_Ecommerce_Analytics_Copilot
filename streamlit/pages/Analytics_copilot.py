import streamlit as st
import pandas as pd

from ai.ai_sql_generator import SQLGenerator
from ai.ai_sql_validator import SQLValidator
from ai.insight_generator import InsightGenerator
from utils.bq_client import run_query

# -----------------------------
# AI Objects
# -----------------------------
sql_generator = SQLGenerator()
insight_generator = InsightGenerator()

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Analytics Copilot",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Analytics Copilot")
st.caption("Ask questions about your business using natural language.")

# -----------------------------
# Session State
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# Sidebar
# -----------------------------
examples = [
    "Average delivery time by city",
    "Top dark stores by revenue",
    "Rider on-time delivery percentage",
    "Customer lifetime value",
    "Order issues by category",
    "Monthly revenue trend",
    "Customer segments",
    "Most sold perishable products",
]

with st.sidebar:

    st.header("Analytics Copilot")

    st.subheader("Try asking")

    for q in examples:
        if st.button(q):
            st.session_state["prefill"] = q

    st.divider()

    if st.button("🗑 Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# -----------------------------
# Display Chat History
# -----------------------------
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        if message["role"] == "assistant":

            if "sql" in message:
                with st.expander("Generated SQL"):
                    st.code(message["sql"], language="sql")

            if "data" in message:
                st.subheader("Results")
                st.dataframe(
                    message["data"],
                    use_container_width=True
                )

                df = message["data"]

                if not df.empty and len(df.columns) >= 2:

                    x = df.columns[0]
                    y = df.columns[1]

                    try:

                        if (
                            "date" in x.lower()
                            or "month" in x.lower()
                            or pd.api.types.is_datetime64_any_dtype(df[x])
                        ) and pd.api.types.is_numeric_dtype(df[y]):

                            st.subheader("📈 Trend")
                            st.line_chart(
                                df.set_index(x)[y],
                                use_container_width=True
                            )

                        elif pd.api.types.is_numeric_dtype(df[y]):

                            st.subheader("📊 Chart")
                            st.bar_chart(
                                df.set_index(x)[y],
                                use_container_width=True
                            )

                    except Exception:
                        pass

            st.subheader("AI Insights")
            st.markdown(message["content"])

        else:
            st.markdown(message["content"])

# -----------------------------
# Chat Input
# -----------------------------
prompt = st.chat_input("Ask a business question...")

if prompt is None:
    prompt = st.session_state.pop("prefill", None)

# -----------------------------
# Pipeline
# -----------------------------
if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            # -----------------------------
            # Generate SQL
            # -----------------------------
            try:
                sql = sql_generator.generate(prompt)
                valid, reason = SQLValidator.validate(sql)

                if not valid:
                    st.error(reason)
                    st.stop()
                with st.expander("Generated SQL"):
                    st.code(sql, language="sql")
                df = run_query(sql)
            except Exception as e:
                st.error(str(e))
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": str(e)
                    }
                )

                st.stop()

            st.subheader("Results")

            st.dataframe(
                df,
                use_container_width=True
            )

            # -----------------------------
            # Auto Charts
            # -----------------------------
            if not df.empty and len(df.columns) >= 2:

                x = df.columns[0]
                y = df.columns[1]

                try:

                    if (
                        "date" in x.lower()
                        or "month" in x.lower()
                        or pd.api.types.is_datetime64_any_dtype(df[x])
                    ) and pd.api.types.is_numeric_dtype(df[y]):

                        st.subheader("📈 Trend")

                        st.line_chart(
                            df.set_index(x)[y],
                            use_container_width=True
                        )

                    elif pd.api.types.is_numeric_dtype(df[y]):

                        st.subheader("📊 Chart")

                        st.bar_chart(
                            df.set_index(x)[y],
                            use_container_width=True
                        )

                except Exception:
                    pass

            # -----------------------------
            # Generate Insights
            # -----------------------------
            summary = insight_generator.generate(
                prompt,
                df
            )

            st.subheader("AI Insights")
            st.markdown(summary)

            # -----------------------------
            # Save Conversation
            # -----------------------------
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": summary,
                    "sql": sql,
                    "data": df,
                }
            )