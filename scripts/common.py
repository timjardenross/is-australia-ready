"""Shared loaders and figure logic for the build and validation scripts."""
import json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
DOC_ORDER = ["d1", "d2", "d4", "d5", "d6"]
CHANGE = "Change or software defect"
PROCESS = "Process or lifecycle failure"


def load(path):
    return json.loads((CONTENT / path).read_text(encoding="utf8"))


def pct(n, d):
    return f"{int(100 * n / d + 0.5)}%"


def derive_f152(outages):
    """Recompute every F152 figure from content/data/outages.json."""
    o = outages
    ch = [r for r in o if r["subtype"] == CHANGE]
    def share(rows):
        sel = [r for r in rows]
        return sel
    ex = [r for r in o if r["subtype"] != "Unclassified"]
    since = [r for r in o if int(r["start"][:4]) >= 2022]
    gb = [r for r in o if r["grade"] == "B"]
    gc = [r for r in o if r["grade"] == "C"]
    power = [r for r in o if r["subtype"] == "Power"]
    proc = [r for r in o if r["subtype"] == PROCESS]
    c = lambda rows: sum(1 for r in rows if r["subtype"] == CHANGE)
    return {
        "outages": len(o),
        "changes": len(ch),
        "share": pct(len(ch), len(o)),
        "share_ex_unclassified": pct(c(ex), len(ex)),
        "share_since_2022": pct(c(since), len(since)),
        "share_grade_b": pct(c(gb), len(gb)),
        "share_grade_c": pct(c(gc), len(gc)),
        "share_power": pct(len(power), len(o)),
        "sens_changes": len(ch) + len(proc),
        "sens_share": pct(len(ch) + len(proc), len(o)),
    }


def load_docs():
    docs = {}
    for slug in DOC_ORDER:
        raw = (CONTENT / "docs" / f"{slug}.md").read_text(encoding="utf8")
        m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
        meta = dict(l.split(": ", 1) for l in m.group(1).split("\n"))
        docs[slug] = {"meta": meta, "body": m.group(2)}
    return docs
