import os
import tempfile
import yaml
import streamlit as st

# Bridge Streamlit Cloud secrets into env vars BEFORE importing pipeline modules
# (summarise.py / deliver.py read os.environ at import time). Locally there may be
# no secrets file, so we fall back to .env via load_dotenv inside those modules.
try:
    for _k, _v in st.secrets.items():
        os.environ[_k] = str(_v)
except Exception:
    pass

from fetch import get_entries
from filter import filter_recent
from summarise import classify, summarise
from build_doc import SECTION_ORDER, _date, build_doc, build_email_html

st.set_page_config(page_title="Daily Health Monitoring", layout="wide")

# Optional password gate (active only if APP_PASSWORD is set in secrets)
try:
    _pw = st.secrets.get("APP_PASSWORD")
except Exception:
    _pw = None
if _pw and st.text_input("Password", type="password") != _pw:
    st.stop()

st.title("Daily Health Monitoring")
st.caption("On-demand health-policy briefing — G20 & G7 Health and Development Partnership.")


def load_sources():
    with open("config.yaml") as f:
        return yaml.safe_load(f)["sources"]


def generate():
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
    return items


def render(it):
    st.markdown(f"**[{it['title']}]({it['link']})**  \n*{it['source']} — {_date(it)}*")
    st.write(it.get("synopsis", ""))


if st.button("Generate today's briefing", type="primary"):
    st.session_state["items"] = generate()

items = st.session_state.get("items")
if not items:
    st.info("Click the button to pull today's news and generate the briefing.")
    st.stop()

accepts = [it for it in items if it["relevance"] == "ACCEPT"]
unsure  = [it for it in items if it["relevance"] == "UNSURE"]

c1, c2, c3 = st.columns(3)
c1.metric("Accepted", len(accepts))
c2.metric("Unsure", len(unsure))
c3.metric("Filtered out", len(items) - len(accepts) - len(unsure))

# Actions: download the Word doc, or send the email
col_a, col_b = st.columns(2)

doc_path = os.path.join(tempfile.gettempdir(), "daily_health_monitoring.docx")
build_doc(items, doc_path)
with open(doc_path, "rb") as f:
    col_a.download_button(
        "Download Word doc", f.read(),
        file_name="daily_health_monitoring.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

if col_b.button("Send as email"):
    try:
        from deliver import send_email
        send_email(subject="Daily Health Monitoring", html_body=build_email_html(items))
        col_b.success("Email sent")
    except Exception as ex:
        col_b.error(f"Email failed: {ex}")

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