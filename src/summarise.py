import os
import time
from dotenv import load_dotenv
from openai import OpenAI, APIError

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

MODEL = "gpt-4o-mini"


# ---- shared LLM call with retry (used by both summarise and classify) ----
def _call(prompt, max_retries=6):
    for attempt in range(max_retries):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.choices[0].message.content.strip()
        except APIError as e:
            wait = 5 * (attempt + 1)
            print(f"  API error ({getattr(e, 'status_code', '?')}) — waiting {wait}s, retrying")
            time.sleep(wait)
    print("  gave up on one item after retries")
    return ""


# ---- summariser ----
SUMMARISE_PROMPT = """You are compiling a daily health-policy monitoring briefing.
Write a concise, factual summary of the article (2-4 sentences). Use a neutral,
professional tone. Where the source makes it clear, your summary should convey:
what was announced or happened; who is involved (the key organisations or people);
and why it matters to the G20 & G7 Health and Development Partnership, whose focus is
global and UK health, health financing and investment, health systems strengthening,
pandemic preparedness, AMR, NCDs and the UN SDGs. Only state a relevance angle where
the article genuinely supports it — never speculate or invent a connection. Include
only information present in the text — no opinions or invented detail. Do not begin
with "This article" — just state what happened.

Here is an example of the desired style:

ARTICLE:
The government has announced that NHS England will be "radically reduced" and
"reshaped", with the size of the centre expected to fall by around half. Three of
NHS England's leading board members — chief financial officer Julian Kelly, chief
operating officer Dame Emily Lawson, and chief delivery officer and national director
for vaccination and screening Steve Russell — have decided to step down in the coming
weeks. Sir James Mackey will set up a transition team within NHS England to lead the
reduction and reshaping of the centre alongside the Department of Health and Social
Care. The changes represent the biggest reshaping of the NHS's national architecture
in more than a decade, part of wider efforts to cut bureaucracy and bring the health
service back under closer political control.

SUMMARY:
The government has announced it will be halving the size of NHS England to ensure
taxpayers' money is being put to the "best possible use." Three of NHS England's
leading board members—chief financial officer Julian Kelly, chief operating officer
Emily Lawson, and chief delivery officer and national director for vaccination and
screening Steve Russell—will also be leaving their posts at the end of March.

Now summarise this article in the same style:

ARTICLE:
{article}

SUMMARY:
"""


def summarise(article_text):
    return _call(SUMMARISE_PROMPT.format(article=article_text))


CLASSIFY_PROMPT = """You are triaging news for a daily monitoring briefing for the G20 & G7 Health
and Development Partnership, which operates at the high-level policy and finance end of global health:
health financing and investment, health systems strengthening, multilateral and ministerial health
policy (G7/G20, WHO, EU, World Bank, IMF, African Union), pandemic preparedness, AMR, NCDs, and the
health-related UN SDGs.

Prioritise high-level policy, financing and structural developments. Skip soft, consumer or single
clinical health news. Reply with exactly one word:

ACCEPT - health POLICY shifts; health FINANCING or economics; structural or health-SYSTEMS change; and
  actions by governments, ministries, parliaments, or multilateral/financing bodies (new funding,
  reforms, strategies, resolutions, major R&D/access or preparedness initiatives). Domestic UK health
  policy and spending count. National disease plans, strategies and frameworks (e.g. a cardiovascular
  or NCD plan) and health-systems guidance are policy and count as ACCEPT, even without a funding figure.
REJECT - soft or consumer health (lifestyle, wellness, diet/exercise, "laughter lowers blood pressure"
  studies), single clinical findings with no policy or systems angle, routine leadership appointments
  or staff changes, local human-interest, sport, entertainment, or anything with no link to health
  policy or financing.
UNSURE - borderline: economic, financial or political news that may bear on health financing but is not
  clearly health; or health news whose policy/systems relevance is unclear. Choose UNSURE for a human.

Examples:
ARTICLE: The World Bank approves a new health-financing facility for low-income countries. -> ACCEPT
ARTICLE: G20 finance ministers back coordinated pandemic-preparedness funding. -> ACCEPT
ARTICLE: MPs debate NHS structural reform and long-term funding. -> ACCEPT
ARTICLE: The government launches a new national cardiovascular disease and stroke plan. -> ACCEPT
ARTICLE: WHO issues guidance for countries to strengthen their health systems. -> ACCEPT
ARTICLE: Study finds laughter may lower blood pressure. -> REJECT
ARTICLE: Ten foods to boost your immune system this winter. -> REJECT
ARTICLE: The Chancellor unveils an autumn budget with changes to public spending. -> UNSURE
ARTICLE: A Premier League club announces a new stadium sponsor. -> REJECT
ARTICLE: The IMF names a new chief economist. -> REJECT

ARTICLE:
{article}

Answer:"""


def classify(article_text):
    answer = _call(CLASSIFY_PROMPT.format(article=article_text)).upper()
    for label in ("ACCEPT", "REJECT", "UNSURE"):
        if label in answer:
            return label
    return "UNSURE"


if __name__ == "__main__":
    tests = [
        "WHO calls for increased investment in global health financing to close the SDG3 funding gap.",
        "How to survive a heatwave: stay hydrated and keep out of the sun, BBC advises.",
        "Treasury announces new funding package for NHS health infrastructure.",
        "Bank of England holds interest rates at 4.5% amid inflation concerns.",
        "Local council opens new community swimming pool this weekend.",
    ]
    for t in tests:
        print(f"{classify(t):8} | {t[:65]}")