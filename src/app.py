import os
import yaml
import streamlit as st

# Bridge Streamlit secrets into env vars (the modules read os.environ at import)
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

from fetch import get_entries
from filter import filter_recent
from summarise import classify, summarise
from build_doc import SECTION_ORDER, _date

st.set_page_config(page_title="Daily Health Monitoring", layout="wide")

# Optional password gate (only active if you set APP_PASSWORD in secrets)
_pw = st.secrets.get("APP_PASSWORD")
if _pw:
    if st.text_input("Password", type="password") != _pw:
        st.stop()

st.title("Daily Health Monitoring")
st.caption("On-demand health-policy briefing — G20 & G7 Health and Development Partnership.")


def load_sources():
    with open("config.yaml") as f:
        return yaml.safe_load(f)["sources"]


def render(it):
    st.markdown(f"**[{it['title']}]({it['link']})**  \n*{it['source']} — {_date(it)}*")
    st.write(it.get("synopsis", ""))


if st.button("Generate today's briefing", type="primary"):
    items = []
    with st.status("Fetching feeds…", expanded=True) as status:
        for s in load_sources():
            try:
                entries = filter_recent(get_entries(s["url"]), hours=24)
            except Exception:
                continue
            for e in entries:
                items.append({
                    "source": s["name"], "section": s["section"],
                    "title": e.get("title", ""), "link": e.get("link", ""),
                    "published_parsed": e.get("published_parsed") or e.get("updated_parsed"),
                    "feed_summary": e.get("summary", ""),
                })

        status.update(label=f"Triaging {len(items)} items…")
        bar = st.progress(0)
        for i, it in enumerate(items, 1):
            it["relevance"] = classify(f"{it['title']}. {it['feed_summary']}")
            bar.progress(i / max(len(items), 1))

        to_sum = [it for it in items if it["relevance"] in ("ACCEPT", "UNSURE")]
        status.update(label=f"Summarising {len(to_sum)} items…")
        for it in to_sum:
            it["synopsis"] = summarise(f"{it['title']}. {it['feed_summary']}")
        status.update(label="Done", state="complete")

    accepts = [it for it in items if it["relevance"] == "ACCEPT"]
    unsure  = [it for it in items if it["relevance"] == "UNSURE"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Accepted", len(accepts))
    c2.metric("Unsure", len(unsure))
    c3.metric("Filtered out", len(items) - len(accepts) - len(unsure))

    for section in SECTION_ORDER:
        sec = [it for it in accepts if it["section"] == section]
        if not sec:
            continue
        st.header(section)
        for it in sec:
            render(it)

    if unsure:
        st.header("Potentially relevant — reviewer discretion")
        for it in unsure:
            render(it)
else:
    st.info("Click the button to pull today's news and generate the briefing.")