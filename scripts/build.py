"""Build the static site into ./site from content/. Run validate.py first (the Action does)."""
import html, json, re, shutil, sys
import markdown
from common import ROOT, CONTENT, DOC_ORDER, load, load_docs

SITE = ROOT / "site"
meta = load("meta.json")
fig = load("figures.json")
sources = load("data/sources.json")
findings = load("data/findings.json")
outages = load("data/outages.json")
docs = load_docs()

NAV = [("index.html", "Brief"), ("d2.html", "Report"), ("d4.html", "Dependencies"), ("d5.html", "Watch"),
       ("d6.html", "Finance and telecom"), ("sources.html", "Sources"), ("findings.html", "Findings"),
       ("register.html", "Outage register"), ("changes.html", "Changes")]
PAGE_FOR = {"d1": "index.html", "d2": "d2.html", "d4": "d4.html", "d5": "d5.html", "d6": "d6.html"}
esc = html.escape

def tokens(text):
    def sub(m):
        grp, key = m.group(1), m.group(2)
        return str(fig[grp][key])
    out = re.sub(r"\{\{(\w+)\.(\w+)\}\}", sub, text)
    return out

ID_RE = re.compile(r"\b(S\d{2}|F\d{2}|T-\d{4}-\d{3})\b")
def link_ids(fragment):
    """Link S/F/T identifiers in text nodes only, never inside an existing anchor."""
    parts = re.split(r"(<[^>]+>)", fragment)
    depth = 0
    for i, p in enumerate(parts):
        if p.startswith("<"):
            if re.match(r"<a\b", p): depth += 1
            elif p.startswith("</a"): depth = max(0, depth - 1)
            continue
        if depth: continue
        def sub(m):
            x = m.group(1)
            page = "sources.html" if x[0] == "S" else ("findings.html" if x[0] == "F" else "register.html")
            return f'<a class="idlink" href="{page}#{x}">{x}</a>'
        parts[i] = ID_RE.sub(sub, p)
    return "".join(parts)

def url_links(s):
    """Turn 'url [locator]; url [locator]' into links."""
    out = []
    for chunk in [c.strip() for c in s.split(";") if c.strip()]:
        m = re.match(r"(https?://\S+)(?:\s*\[(.*)\])?$", chunk)
        if m: out.append(f'<a href="{esc(m.group(1))}" rel="noopener">{esc(m.group(2) or "link")}</a>')
        else: out.append(esc(chunk))
    return "; ".join(out)

def sources_table():
    rows = []
    for r in sources:
        title = esc(r["title"])
        if r["url"]: title = f'<a href="{esc(r["url"])}" rel="noopener">{title}</a>'
        rows.append(f'<tr id="{r["source_id"]}"><td><b>{r["source_id"]}</b></td><td>{title}</td><td>{esc(r["publisher"])}</td>'
                    f'<td>{esc(r["publication_date"])}</td><td>{esc(r["source_type"])}</td><td>{esc(r["locator"])}</td>'
                    f'<td>{esc(r["finding_supported"])}</td><td>{esc(r["limits"])}</td></tr>')
    head = "<tr><th>ID</th><th>Source</th><th>Publisher</th><th>Date</th><th>Type</th><th>Locator</th><th>Supports</th><th>Limit</th></tr>"
    return f'<div class="tablewrap"><table class="data" data-filter><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table></div>'

def findings_table():
    rows = []
    for r in findings:
        rows.append(f'<tr id="{r["ID"]}"><td><b>{r["ID"]}</b></td><td>{esc(r["theme"])}</td><td>{esc(r["finding"])}</td>'
                    f'<td>{esc(r["source_IDs"])}</td><td>{esc(r["status_classification"])}</td><td>{esc(r["confidence"])}</td>'
                    f'<td>{esc(r["implementation_status_as_of_19_Nov_2026"])}</td><td>{esc(r["uncertainty_next_verification"])}</td></tr>')
    head = "<tr><th>ID</th><th>Theme</th><th>Finding</th><th>Sources</th><th>Status</th><th>Confidence</th><th>Implementation status</th><th>Next check</th></tr>"
    return f'<div class="tablewrap"><table class="data" data-filter><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table></div>'

def register_table():
    rows = []
    for r in outages:
        srcs = " ".join(f'<a href="{esc(u)}" rel="noopener">{i+1}</a>' for i, u in enumerate(r["sources"]))
        rows.append(f'<tr id="{r["id"]}"><td><b>{r["id"]}</b></td><td>{esc(r["start"])}</td><td>{esc(r["name"])}</td><td>{esc(r["operator"])}</td>'
                    f'<td>{esc(r["region"])}</td><td>{esc(r["subtype"])}</td><td>{esc(r["cause_status"])}</td><td>{esc(r["grade"])}</td>'
                    f'<td>{esc(r["tier"])}</td><td>{esc(r["au_exposure"])}</td><td>{srcs}</td></tr>')
    head = "<tr><th>ID</th><th>Start</th><th>Event</th><th>Operator</th><th>Region</th><th>Cause type</th><th>Cause status</th><th>Grade</th><th>Tier</th><th>AU exposure</th><th>Sources</th></tr>"
    return f'<div class="tablewrap"><table class="data" data-filter><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table></div>'

def page(fname, title, body, toc=""):
    nav = "".join(f'<a href="{h}"{" class=on" if h == fname else ""}>{esc(t)}</a>' for h, t in NAV)
    side = f'<aside class="toc"><div class="toch">On this page</div>{toc}</aside>' if toc else ""
    return f"""<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} | {esc(meta['site_title'])}</title><link rel="stylesheet" href="style.css"></head><body>
<header><div class="wrap"><a class="brand" href="index.html"><b>{esc(meta['site_title'])}</b> <span>{esc(meta['subtitle'])}</span></a><nav>{nav}</nav></div></header>
<main class="wrap{' has-toc' if toc else ''}">{side}<article>{body}</article></main>
<footer><div class="wrap"><p>Revision {esc(meta['revision'])}, released {esc(meta['released'])}. Evidence cutoff {esc(meta['evidence_cutoff'])}. Public-source assessment by {esc(meta['author'])}.</p>
<p>{esc(meta['disclosure'])}</p><p><a href="changes.html">Change log</a> · <a href="data/sources.json">sources.json</a> · <a href="data/findings.json">findings.json</a> · <a href="data/outages.json">outages.json</a></p></div></footer>
<script src="site.js"></script></body></html>"""

def render_doc(slug):
    d = docs[slug]
    md = markdown.Markdown(extensions=["tables", "sane_lists", "toc"], extension_configs={"toc": {"toc_depth": "2-3"}})
    body = md.convert(tokens(d["body"]))
    body = body.replace("<p>{{catalogue_table}}</p>", sources_table()).replace("<p>{{findings_table}}</p>", findings_table())
    assert "{{" not in body, f"unresolved token in {slug}"
    body = re.sub(r"<table>", '<div class="tablewrap"><table>', body); body = body.replace("</table>", "</table></div>")
    body = link_ids(body)
    head = f'<p class="kicker">{esc(d["meta"]["kicker"])}</p><h1>{esc(d["meta"]["title"])}</h1>'
    toc = md.toc if slug == "d2" or body.count("<h2") > 3 else ""
    return page(PAGE_FOR[slug], d["meta"]["title"], head + body, toc)

def main():
    if SITE.exists(): shutil.rmtree(SITE)
    (SITE / "data").mkdir(parents=True)
    for slug in DOC_ORDER:
        (SITE / PAGE_FOR[slug]).write_text(render_doc(slug), encoding="utf8")
    intro = lambda t: f"<h1>{t}</h1>"
    (SITE / "sources.html").write_text(page("sources.html", "Source catalogue", intro("Source catalogue") +
        f"<p>{len(sources)} sources (S01 to S{len(sources):02d}). Each citation in the report links to its row here. Filter by any word.</p>" +
        '<input class="filter" placeholder="Filter sources" aria-label="Filter sources">' + sources_table()), encoding="utf8")
    (SITE / "findings.html").write_text(page("findings.html", "Findings register", intro("Findings register") +
        f"<p>{len(findings)} findings (F01 to F{len(findings):02d}) with status, confidence and next verification step.</p>" +
        '<input class="filter" placeholder="Filter findings" aria-label="Filter findings">' + findings_table()), encoding="utf8")
    f = fig["f152"]
    summ = (f'<div class="callout"><b>F152.</b> Change or software defects are the largest single cause of large outages: '
            f'{f["changes"]} of {f["outages"]} sampled outages ({f["share"]}). Not a majority. The register is a curated sample, not a census. '
            f'Rows with a primary or official source show {f["share_grade_b"]}; rows with secondary sources only show {f["share_grade_c"]}. '
            f'Figures are computed from the rows below. See the <a href="d2.html">report</a>, section 8.</div>')
    (SITE / "register.html").write_text(page("register.html", "Outage register", intro("Outage register") + summ +
        '<input class="filter" placeholder="Filter outages" aria-label="Filter outages">' + register_table()), encoding="utf8")
    rows = "".join(f"<tr><td>{esc(c['date'])}</td><td>{esc(c['revision'])}</td><td>{esc(c['change'])}</td></tr>" for c in meta["changelog"])
    (SITE / "changes.html").write_text(page("changes.html", "Change log", intro("Change log") +
        f'<div class="tablewrap"><table class="data"><thead><tr><th>Date</th><th>Revision</th><th>Change</th></tr></thead><tbody>{rows}</tbody></table></div>'), encoding="utf8")
    for n in ("sources", "findings", "outages"):
        shutil.copy(CONTENT / "data" / f"{n}.json", SITE / "data" / f"{n}.json")
    shutil.copy(ROOT / "assets" / "style.css", SITE / "style.css")
    shutil.copy(ROOT / "assets" / "site.js", SITE / "site.js")
    (SITE / ".nojekyll").write_text("")
    print("built", len(list(SITE.glob("*.html"))), "pages")

main()
