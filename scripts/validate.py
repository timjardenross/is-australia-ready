"""Integrity checks. Exit 1 on any failure. Run before every build."""
import json, re, sys
from common import CONTENT, DOC_ORDER, load, load_docs, derive_f152

errors = []
def fail(msg): errors.append(msg)

sources = load("data/sources.json"); findings = load("data/findings.json"); outages = load("data/outages.json")
meta = load("meta.json"); fig = load("figures.json"); docs = load_docs()
sid = [r["source_id"] for r in sources]; fid = [r["ID"] for r in findings]; tid = [r["id"] for r in outages]

# 1. unique IDs, expected shape
for name, ids in (("source", sid), ("finding", fid), ("outage", tid)):
    if len(ids) != len(set(ids)): fail(f"duplicate {name} IDs")
for r in sources:
    if r["url"] and not r["url"].startswith("https://"): fail(f"{r['source_id']}: url is not https")
    if not r["url"] and r["source_id"] != "S45": fail(f"{r['source_id']}: missing url")

# 2. citations in prose resolve, and every catalogue entry is cited
text = ""
for slug in DOC_ORDER:
    body = docs[slug]["body"]
    body = "\n".join(l for l in body.split("\n") if not l.startswith("The following catalogue reproduces"))
    text += body + "\n"
cited = set(re.findall(r"\bS(\d{2})\b", text))
for a, b in re.findall(r"\bS(\d{2})[–-]S?(\d{2})\b", text):
    cited |= {f"{i:02d}" for i in range(int(a), int(b) + 1)}
for c in sorted(cited):
    if f"S{c}" not in sid: fail(f"cited S{c} is not in the catalogue")
for s in sid:
    if s[1:] not in cited: fail(f"{s} is in the catalogue but never cited")
for c in set(re.findall(r"\bF(\d{2})\b", text)):
    if f"F{c}" not in fid: fail(f"cited F{c} is not in the findings register")
for c in set(re.findall(r"\bT-\d{4}-\d{3}\b", text)):
    if c not in tid: fail(f"cited {c} is not in the outage register")
for r in findings:
    for s in re.findall(r"S\d{2}", r["source_IDs"]):
        if s not in sid: fail(f"{r['ID']} cites unknown {s}")

# 3. figures equal what the data produces; tokens resolve
derived = derive_f152(outages)
for k, v in derived.items():
    if fig["f152"].get(k) != v: fail(f"figures.json f152.{k} is {fig['f152'].get(k)!r}, data gives {v!r}. Run scripts/recompute_figures.py")
for m in re.finditer(r"\{\{(\w+)\.(\w+)\}\}", text):
    if m.group(1) not in fig or m.group(2) not in fig[m.group(1)]: fail(f"unknown figure token {m.group(0)}")
for tok in re.findall(r"\{\{(\w+)\}\}", text):
    if tok not in ("catalogue_table", "findings_table"): fail(f"unknown token {{{{{tok}}}}}")

# 4. stale phrases
for line in (CONTENT / "stale_phrases.txt").read_text(encoding="utf8").splitlines():
    if not line.strip() or line.startswith("#"): continue
    hay = text + json.dumps(sources) + json.dumps(findings) + json.dumps(meta)
    if re.search(line, hay): fail(f"stale phrase matched: {line}")

# 5. required metadata
for k in ("site_title", "subtitle", "evidence_cutoff", "revision", "released", "disclosure", "changelog"):
    if not meta.get(k): fail(f"meta.json missing {k}")
if meta["changelog"] and meta["changelog"][0]["date"] < max(c["date"] for c in meta["changelog"]):
    fail("changelog must list the newest entry first")

if errors:
    print(f"VALIDATION FAILED ({len(errors)}):"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"validation passed: {len(sid)} sources all cited, {len(fid)} findings, {len(tid)} outages, figures match data, no stale phrases")
