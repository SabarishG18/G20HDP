import os
import time
import yaml
from fetch import get_entries
from filter import filter_recent
from summarise import summarise, classify, editor_note, pick_lead
from build_doc import build_email_html, build_pdf
from deliver import send_email
from dedup import deduplicate


def load_sources(path="config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)["sources"]


def collect_items(sources, hours=24):
    items = []
    for source in sources:
        try:
            entries = filter_recent(get_entries(source["url"]), hours=hours)
        except Exception as ex:
            print(f"  ! {source['name']} failed ({type(ex).__name__}) — skipped")
            continue
        for e in entries:
            items.append({
                "source": source["name"],
                "section": source["section"],
                "title": e.get("title", ""),
                "link": e.get("link", ""),
                "published_parsed": e.get("published_parsed") or e.get("updated_parsed"),
                "feed_summary": e.get("summary", ""),
            })
        print(f"  {source['name']}: {len(entries)}")
    return items


if __name__ == "__main__":
    sources = load_sources()
    print("Fetching…")
    items = collect_items(sources, hours=24)

    items = deduplicate(items)
    print(f"\n{len(items)} unique stories after removing duplicates")

    print(f"\nTriaging {len(items)} items…")
    for i, it in enumerate(items, 1):
        it["relevance"] = classify(f"{it['title']}. {it['feed_summary']}")
        print(f"  {i}/{len(items)} — {it['relevance']:7} — {it['source']}: {it['title'][:200]}")

    # Only summarise what we'll actually show in full (accepts + unsures)
    to_summarise = [it for it in items if it["relevance"] in ("ACCEPT", "UNSURE")]
    print(f"\nSummarising {len(to_summarise)} items…")
    for i, it in enumerate(to_summarise, 1):
        it["synopsis"] = summarise(f"{it['title']}. {it['feed_summary']}")
        print(f"  {i}/{len(to_summarise)} — {it['source']}: {it['title'][:200]}")

    # Editorial layer: editor's note + lead story (from the accepted items)
    accepts = [it for it in items if it["relevance"] == "ACCEPT"]
    print("\nWriting the editor's note and choosing the lead story…")
    note = editor_note(accepts)
    lead, lead_why = pick_lead(accepts)

    html_body = build_email_html(items, note=note, lead=lead, lead_why=lead_why)

    os.makedirs("output", exist_ok=True)
    filename = os.path.join("output", f"daily_monitoring_{time.strftime('%Y-%m-%d')}.pdf")
    build_pdf(html_body, filename)

    send_email(
        subject=f"Daily Health Monitoring — {time.strftime('%d %b %Y')}",
        html_body=html_body,
        attachment_path=filename if os.path.exists(filename) else None,
    )
    print("Emailed.")

    a = sum(1 for it in items if it["relevance"] == "ACCEPT")
    u = sum(1 for it in items if it["relevance"] == "UNSURE")
    r = sum(1 for it in items if it["relevance"] == "REJECT")
    print(f"Done — {a} accepted, {u} unsure, {r} rejected → {filename}")