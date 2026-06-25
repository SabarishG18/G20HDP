import yaml
import feedparser
from fetch import USER_AGENT

with open("config.yaml") as f:
    sources = yaml.safe_load(f)["sources"]

print(f"{'SOURCE':28} {'ITEMS':>5} {'HTTP':>5} {'bozo':>4}  note")
print("-" * 72)
for s in sources:
    parsed = feedparser.parse(s["url"], agent=USER_AGENT)
    n = len(parsed.entries)
    status = parsed.get("status", "?")
    bozo = int(parsed.get("bozo", 0))

    note = ""
    if n == 0:
        if status == 404:
            note = "404 — URL wrong"
        elif status in (301, 302, 308):
            note = f"redirect ({status}) — try the new URL"
        elif bozo:
            note = "not valid XML — probably an HTML page, not a feed"
        else:
            note = "parsed OK but empty"
    print(f"{s['name']:28} {n:>5} {str(status):>5} {bozo:>4}  {note}")