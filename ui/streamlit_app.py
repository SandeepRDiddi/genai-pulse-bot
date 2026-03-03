import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="GenAI Global Trends Bot", page_icon="🌍", layout="wide")
st.title("🌍 GenAI Global Trends Bot")
st.caption("Global GenAI updates (GDELT + Media Cloud + optional RSS). Grounded answers with citations.")

tab_chat, tab_lead, tab_bus, tab_tech = st.tabs(["Chat", "Leadership Brief", "Business Brief", "Tech Brief"])

with st.sidebar:
    st.subheader("Settings")
    api_url = st.text_input("API URL", API_URL)
    top_k = st.slider("Top-K sources", 3, 20, 8)
    if st.button("Health Check"):
        try:
            r = requests.get(api_url.rstrip("/") + "/health", timeout=10)
            st.success(r.json())
        except Exception as e:
            st.error(str(e))
    st.divider()
    st.markdown("**Ingest latest content**")
    st.code("python -m app.ingest --once")

def call_brief(persona: str):
    r = requests.get(api_url.rstrip("/") + f"/briefing/{persona}", timeout=120)
    r.raise_for_status()
    return r.json()

with tab_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Ask a question (e.g., 'What are the latest enterprise agent trends?')")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    r = requests.post(
                        api_url.rstrip("/") + "/chat",
                        json={"query": prompt, "top_k": int(top_k)},
                        timeout=180,
                    )
                    r.raise_for_status()
                    data = r.json()
                    st.markdown(data["answer"])
                    if data.get("sources"):
                        st.markdown("---")
                        st.markdown("**Sources**")
                        for idx, s in enumerate(data["sources"], start=1):
                            pub = s.get("published") or ""
                            src = s.get("source") or ""
                            st.markdown(f"[{idx}] [{s['title']}]({s['url']}) — {src} {pub}")
                    st.session_state.messages.append({"role": "assistant", "content": data["answer"]})
                except Exception as e:
                    st.error(f"Request failed: {e}")

def render_brief(tab, persona, title):
    with tab:
        st.subheader(title)
        if st.button(f"Refresh {title}", key=f"refresh-{persona}"):
            st.session_state[f"brief-{persona}"] = None
        if st.session_state.get(f"brief-{persona}") is None:
            with st.spinner("Generating briefing..."):
                try:
                    st.session_state[f"brief-{persona}"] = call_brief(persona)
                except Exception as e:
                    st.error(str(e))
                    return
        data = st.session_state.get(f"brief-{persona}")
        if not data:
            return
        st.markdown(data["briefing"])
        st.markdown("---")
        st.markdown("**Sources**")
        for idx, s in enumerate(data.get("sources", []), start=1):
            pub = s.get("published") or ""
            src = s.get("source") or ""
            st.markdown(f"[{idx}] [{s['title']}]({s['url']}) — {src} {pub}")

render_brief(tab_lead, "leadership", "Leadership Brief (5 min)")
render_brief(tab_bus, "business", "Business Brief")
render_brief(tab_tech, "tech", "Tech Brief")
