import streamlit as st
from pipeline import run
from llm import usage_log

st.set_page_config(page_title="Stale-Answer Detector", page_icon="🕒", layout="wide")

st.title("🕒 Stale-Answer Detector")
st.caption("Paste an AI-generated answer. Tavily checks each time-sensitive claim "
           "against live web sources, and Bifrost routes every model call.")

DEFAULT = ("Twitter's CEO is Jack Dorsey, and the platform is still called Twitter. "
           "ChatGPT Plus costs $20 per month. Paris is the capital of France.")

answer = st.text_area("AI-generated answer to check:", value=DEFAULT, height=150)

ICON = {"FRESH": "🟢", "UNCERTAIN": "🟡", "STALE": "🔴"}

if st.button("Check freshness", type="primary"):
    usage_log.clear()
    with st.spinner("Extracting claims, searching the live web, verifying... (about a minute)"):
        try:
            results = run(answer)
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.stop()

    if not results:
        st.info("No time-sensitive claims were found in this answer.")
    else:
        stale = sum(1 for r in results if r["label"] == "STALE")
        fresh = sum(1 for r in results if r["label"] == "FRESH")
        c1, c2, c3 = st.columns(3)
        c1.metric("Claims checked", len(results))
        c2.metric("Stale", stale)
        c3.metric("Fresh", fresh)

    for r in results:
        title = f"{ICON[r['label']]} {r['label']}  ({r['score']}/100)  -  {r['claim']}"
        with st.expander(title, expanded=True):
            st.write(f"**Category:** {r['category']}  |  **Verdict:** {r['verdict']}  |  "
                     f"**Confidence:** {r['confidence']}")
            st.write(f"**What is true today:** {r['current_fact']}")
            st.write(f"**Why:** {r['reasoning']}")
            if r.get("best_source_url"):
                st.markdown(f"**Best source:** [{r['best_source_url']}]({r['best_source_url']})")
            with st.expander("All sources Tavily found"):
                for s in r["sources"]:
                    st.markdown(f"- [{s['title']}]({s['url']})")

    st.sidebar.header("Bifrost gateway stats")
    st.sidebar.metric("Model calls", len(usage_log))
    st.sidebar.metric("Total tokens", sum(u["tokens"] for u in usage_log))
    st.sidebar.metric("Total seconds", round(sum(u["seconds"] for u in usage_log), 1))
    st.sidebar.write("Every call below went through Bifrost:")
    st.sidebar.dataframe(usage_log)