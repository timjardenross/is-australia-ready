"""Rewrite the derived F152 figures in content/figures.json from content/data/outages.json.
Static values (register row count, test reach) are kept as they are and edited by hand."""
import json
from common import CONTENT, load, derive_f152

fig_path = CONTENT / "figures.json"
fig = json.loads(fig_path.read_text(encoding="utf8")) if fig_path.exists() else {"f152": {}, "ausalert": {}}
fig["f152"].update(derive_f152(load("data/outages.json")))
fig_path.write_text(json.dumps(fig, indent=2, ensure_ascii=False) + "\n", encoding="utf8")
print("figures.json updated:", {k: v for k, v in fig["f152"].items()})
