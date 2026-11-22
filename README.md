# Is Australia Ready?

National resilience, preparedness and systemic risk, 2026. An independent public-source assessment by TJR.

Live site: https://timjardenross.github.io/is-australia-ready/

The site is built from structured files in `content/`. Change one file and the whole site stays consistent.

## What lives where

| Path | What it holds | Edit it to |
|---|---|---|
| `content/docs/d1.md` to `d6.md` | The five documents (Brief, Report, Dependencies, Watch, Finance and telecom annex) | Change prose |
| `content/data/sources.json` | Source catalogue S01 to S56 | Add or correct a source |
| `content/data/findings.json` | Findings register F01 to F45 | Change a finding's status or next check |
| `content/data/outages.json` | The 90 outage rows behind finding F152 | Add or regrade an outage |
| `content/figures.json` | Figures used in prose (`{{f152.share}}` and similar) | Change a static value (derived values are recomputed) |
| `content/meta.json` | Revision, cutoff, disclosure, change log | Record each release |
| `content/stale_phrases.txt` | Regexes that must never appear | Add a phrase once it has been retired |

Prose pulls figures with tokens such as `{{f152.share}}`. IDs such as S33, F35 and T-2026-023 become links automatically.

## Update routine

```bash
pip install -r requirements.txt
python scripts/recompute_figures.py   # only if outages.json changed
python scripts/validate.py            # IDs, citations, figures, stale text
python scripts/build.py               # writes ./site
```

Then add a line to `changelog` in `content/meta.json` and push to `main`. The GitHub Action validates, builds and deploys. A failed check blocks the deploy.

## What the checks enforce

- Every cited S, F and T ID exists, and every catalogue source is cited somewhere.
- Every F152 figure equals what `outages.json` produces.
- No unresolved figure tokens, and none of the retired phrases.
- Catalogue URLs are https, and the change log lists the newest entry first.

## Scope

Public-source assessment. Evidence cutoff 19 November 2026. Findings are about public assurance, not about whether any system would fail.
