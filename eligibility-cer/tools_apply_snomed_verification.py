#!/usr/bin/env python3
"""Record SNOMED CT verification results (from the Snowstorm connector) into the terminology seed bundle.
Usage: python tools_apply_snomed_verification.py results.json   where results.json = {code: {"active": bool, "display": str}}"""
import json, sys
B = "terminology/seed-bundle.json"
res = json.load(open(sys.argv[1]))
b = json.load(open(B, encoding="utf-8"))
b["code_systems"]["SNOMED CT"]["version"] = "http://snomed.info/sct/900000000000207008/version/20261001 (as reported by the snomedct-us branch on Snowstorm)"
n = 0
for c in b["concepts"]:
    p = c["primary"]
    if p["system"] != "SNOMED CT" or p["code"] not in res:
        continue
    r = res[p["code"]]
    c["verification"] = {"source": "SNOMED CT US Edition via Snowstorm (snomedbrowser.org)", "release": "20261001",
                         "checked": "2026-10-07", "active": r["active"], "official_display": r.get("display")}
    if r["active"] and r.get("display"):
        p["display"] = r["display"]
    n += 1
b["warning"] = ("SNOMED CT codes verified active against the US Edition 20261001 (existence/status only; mapping meaning and "
                "relationship still need terminology-lead review). LOINC and HGNC codes remain UNVERIFIED seed values. "
                "NCIt and UMLS CUI links are empty.")
json.dump(b, open(B, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"verified {n} SNOMED concepts")
