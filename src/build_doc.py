import time
import html
from docx import Document

SECTION_ORDER = [
    "International and Multinational Organisations",
    "G20 and G7",
    "UK and EU Government",
    "Think Tanks",
    "International Health Organisations",
    "Academic Organisations",
    "Media Organisations",
]


def _date(it):
    return time.strftime("%d/%m/%y", it["published_parsed"]) if it["published_parsed"] else "n/a"

def _email_item_html(it):
    source   = html.escape(it["source"])
    title    = html.escape(it["title"])
    synopsis = html.escape(it.get("synopsis", ""))
    link     = html.escape(it["link"], quote=True)
    return (f'<p><strong>{source} — {_date(it)} — '
            f'<a href="{link}">{title}</a></strong><br>{synopsis}</p>')


def build_email_html(items):
    accepts = [it for it in items if it["relevance"] == "ACCEPT"]
    unsure  = [it for it in items if it["relevance"] == "UNSURE"]

    parts = ["<h1>Daily Health Monitoring</h1>"]
    for section in SECTION_ORDER:
        section_items = [it for it in accepts if it["section"] == section]
        if not section_items:
            continue
        parts.append(f"<h2>{html.escape(section)}</h2>")
        parts.extend(_email_item_html(it) for it in section_items)

    if unsure:
        parts.append("<h2>Potentially relevant — reviewer discretion</h2>")
        parts.extend(_email_item_html(it) for it in unsure)

    return "\n".join(parts)


def build_doc(items, filename):
    doc = Document()
    doc.add_heading("Daily Health Monitoring", level=0)

    accepts = [it for it in items if it["relevance"] == "ACCEPT"]
    unsure  = [it for it in items if it["relevance"] == "UNSURE"]

    # Accepted — grouped by section, full synopsis
    for section in SECTION_ORDER:
        section_items = [it for it in accepts if it["section"] == section]
        if not section_items:
            continue
        doc.add_heading(section, level=1)
        for it in section_items:
            doc.add_heading(f"{it['source']} — {_date(it)} — {it['title']}", level=2)
            doc.add_paragraph(it.get("synopsis", ""))
            doc.add_paragraph(it["link"])

    # Unsure — flagged for human review
    if unsure:
        doc.add_heading("Potentially relevant — reviewer discretion", level=1)
        for it in unsure:
            doc.add_heading(f"{it['source']} — {_date(it)} — {it['title']}", level=2)
            doc.add_paragraph(it.get("synopsis", ""))
            doc.add_paragraph(it["link"])

    doc.save(filename)