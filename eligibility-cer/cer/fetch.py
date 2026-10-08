"""Fetch studies from ClinicalTrials.gov API v2 (needs outbound access to clinicaltrials.gov)."""
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BASE = "https://clinicaltrials.gov/api/v2/studies"


def _get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "eligibility-cer/0.1"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_study(nct):
    d = _get(f"{BASE}/{nct}?format=json")
    d["_provenance"] = {"retrieved_via": "ct.gov API v2", "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    return d


def search(condition, status="RECRUITING", phase=None, n=10):
    q = {"query.cond": condition, "filter.overallStatus": status, "pageSize": n,
         "fields": "NCTId,BriefTitle,OverallStatus,Phase,EligibilityCriteria"}
    if phase:
        q["filter.advanced"] = f"AREA[Phase]{phase}"
    d = _get(BASE + "?" + urllib.parse.urlencode(q))
    return [(s["protocolSection"]["identificationModule"]["nctId"], s["protocolSection"]["identificationModule"].get("briefTitle", ""))
            for s in d.get("studies", [])]
