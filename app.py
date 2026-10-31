"""Streamlit UI for AI Student Support Agent. Run: streamlit run app.py"""
import os, json
import streamlit as st
from agent import answer, DB_PATH, load_memory, TRACE_PATH

st.set_page_config(page_title="AI Student Support Agent", page_icon="🎓", layout="wide")
st.title("AI Student Support Agent")
st.caption("Student records • Fees • Scholarships • Exams • Timetables • Academic calendar")
if not DB_PATH.exists():
    st.error("college.db is missing. Run `python setup_db.py` first.")
    st.stop()

with st.sidebar:
    st.subheader("Session")
    session_id = st.text_input("Student session ID", value="default").strip() or "default"
    st.caption("Only low-risk profile facts (preferred name, programme, semester) are kept in student_memory.json.")
    st.subheader("Try a question")
    samples = [
        "What is my current fee status? My student ID is S1004.",
        "The payment portal failed. Can I pay on the next working day?",
        "What scholarship status is recorded for S1004?",
        "Show Semester I exams.",
        "Show my Semester II timetable for Monday.",
        "What academic events are listed in November 2026?",
    ]
    for q in samples:
        if st.button(q, use_container_width=True):
            st.session_state["pending_prompt"] = q

if "messages" not in st.session_state:
    st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("trace"):
            with st.expander("Execution trace"):
                st.json(m["trace"])

prompt = st.chat_input("Ask the student support agent...")
if st.session_state.get("pending_prompt"):
    prompt = st.session_state.pop("pending_prompt")
if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Checking the relevant records and policy..."):
            reply, trace = answer(prompt, session_id, st.session_state.messages[:-1])
        st.markdown(reply)
        with st.expander("Execution trace — printed for every query"):
            st.json(trace)
    st.session_state.messages.append({"role":"assistant","content":reply,"trace":trace})

st.divider()
st.subheader("Latest run measurements")
if TRACE_PATH.exists():
    lines = TRACE_PATH.read_text(encoding="utf-8").splitlines()
    if lines:
        try:
            latest = json.loads(lines[-1])
            cols = st.columns(4)
            cols[0].metric("Latency", f'{latest.get("latency_seconds",0)} s')
            cols[1].metric("Tool calls", len(latest.get("tools_used",[])))
            cols[2].metric("Tokens", latest.get("total_tokens",0))
            cols[3].metric("Retrieved sections", len(latest.get("retrieved_evidence",[])))
            st.json(latest)
        except json.JSONDecodeError:
            st.info("Trace file exists but the latest line is invalid JSON.")
    else:
        st.info("No query has been run yet.")
else:
    st.info("No trace has been recorded yet.")
