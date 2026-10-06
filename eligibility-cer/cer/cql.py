"""Deterministic CER -> CQL compiler (reference projection) for a *declared, tested subset*.

Supported leaves : age; ECOG (LOINC proposal); lab/measurement with a LOINC binding (value compare, x-ULN
                   using the result's own reference range).
Everything else  : emitted as `null` with an UNSUPPORTED comment and listed in the manifest -- never approximated.
Safety rules mirrored from the evaluator:
  * missing / non-final / stale evidence -> null (unknown), never false
  * an exception or unresolved temporal anchor keeps a positive result null
  * polarity applied once, at the criterion root: inclusion = cond, exclusion = not cond
  * CQL and/or/not are Kleene three-valued, matching ALL/ANY/NOT
  * criteria that are not `validated` compile to null unless allow_draft=True (draft banner added)
The output has NOT been run through the CQL-to-ELM translator in this environment: pin and test it
(translator + engine + FHIRHelpers versions) before any use.
"""
import hashlib
import re

from .extract import LABS, slug

ECOG_LOINC = ("89247-1", "ECOG Performance Status score")   # proposed_unreviewed
STATUSES = "{'final', 'amended', 'corrected'}"
UNIT_OK = re.compile(r"^[A-Za-z0-9*/%.\[\]()+\-^]+$")


class _Unsupported(Exception):
    pass


def _cmp(c):
    return {">=": ">=", "<=": "<=", ">": ">", "<": "<", "=": "="}[c]


class Compiler:
    def __init__(self, cer, scope=None, allow_draft=False):
        self.cer, self.scope, self.allow_draft = cer, scope, allow_draft
        self.defs, self.helpers, self.codes, self.params = [], {}, {}, {}
        self.unsupported, self.executable, self.n = [], 0, 0
        self.helper_defs = []

    # -- helpers -------------------------------------------------------------------------------
    def _code(self, name, loinc, display):
        cname = f"{name} ({loinc})"
        self.codes[cname] = f"code \"{cname}\": '{loinc}' from \"LOINC\" display '{display}'"
        return cname

    def _latest(self, analyte, loinc, display, anchor=None, window=None):
        key = (analyte, anchor, tuple(window) if window else None)
        if key in self.helpers:
            return self.helpers[key]
        cname = self._code(analyte, loinc, display)
        name = f"{analyte} latest" + (f" in window {len(self.helpers)}" if window else "")
        if window:
            a = self._anchor_param(anchor)
            when = f"FHIRHelpers.ToDateTime(O.effective as FHIR.dateTime) in Interval[\"{a}\" - {int(window[0])} {window[1]}s, \"{a}\"]"
        else:
            when = "days between FHIRHelpers.ToDateTime(O.effective as FHIR.dateTime) and \"ScreeningDate\" in Interval[0, \"LabMaxAgeDays\"]"
            self.params.setdefault("ScreeningDate", "parameter \"ScreeningDate\" DateTime  // no default on purpose: a missing anchor is unknown, not today")
            self.params.setdefault("LabMaxAgeDays", "parameter \"LabMaxAgeDays\" Integer default 90  // site evidence-freshness policy")
        self.helper_defs.append(
            f"define \"{name}\":\n  Last([Observation: \"{cname}\"] O\n    where O.status.value in {STATUSES}\n      and {when}\n    sort by FHIRHelpers.ToDateTime(effective as FHIR.dateTime))")
        self.helpers[key] = name
        return name

    def _anchor_param(self, anchor):
        pname = f"{slug(anchor).title().replace('_', '')}Date"
        self.params.setdefault(pname, f"parameter \"{pname}\" DateTime  // anchor '{anchor}'; no default")
        return pname

    # -- leaves --------------------------------------------------------------------------------
    def _leaf(self, n):
        p = n["predicate"]
        k = p["kind"]
        if n.get("applicability"):
            raise _Unsupported("conditional applicability needs an explicit applicability fact")
        tw = n.get("time_window")
        window = None
        if tw:
            if tw.get("status") != "parsed" or tw.get("direction") != "lookback" or tw.get("value") is None:
                raise _Unsupported("temporal anchor missing/unresolved")
            window, anchor = (tw["value"], tw["unit"]), tw["anchor"]
        else:
            anchor = None
        if k == "age":
            return f"AgeInYears() {_cmp(p['comparator'])} {int(p['value'])}"
        if k == "ecog":
            lat = self._latest("ECOG", *ECOG_LOINC, anchor=anchor, window=window)
            vals = ", ".join(str(v) for v in p["allowed_values"])
            return f"if \"{lat}\" is null then null\n    else FHIRHelpers.ToInteger(\"{lat}\".value as FHIR.integer) in {{{vals}}}"
        if k in ("lab", "measurement"):
            t = p.get("terminology", {})
            if t.get("system") != "LOINC":
                raise _Unsupported(f"no LOINC binding for '{p['analyte']}' (terminology unbound)")
            if window:
                raise _Unsupported("lab with explicit window not in the tested subset")
            lat = self._latest(p["analyte"], t["code"], p["analyte"], None, None)
            if p.get("uln_multiple"):
                rr = f"\"{lat}\".referenceRange[0].high.value"
                return (f"if \"{lat}\" is null or {rr} is null then null\n    else FHIRHelpers.ToDecimal((\"{lat}\".value as FHIR.Quantity).value)"
                        f" {_cmp(p['comparator'])} {p['value']:g} * FHIRHelpers.ToDecimal({rr})")
            u = p.get("unit")
            if not u or not UNIT_OK.match(u):
                raise _Unsupported("unit missing or not UCUM-like")
            return f"if \"{lat}\" is null then null\n    else FHIRHelpers.ToQuantity(\"{lat}\".value as FHIR.Quantity) {_cmp(p['comparator'])} {p['value']:g} '{u}'"
        if k == "biomarker":
            raise _Unsupported("biomarker: needs site genomic mapping / molecular matcher with assay & specimen adequacy")
        if k == "condition":
            raise _Unsupported(f"condition '{p['concept']}' has no terminology binding / evidence-adequacy policy")
        raise _Unsupported(f"predicate kind '{k}'")

    # -- tree ----------------------------------------------------------------------------------
    def _expr(self, n, tag):
        """returns CQL expression string (Boolean) or raises _Unsupported"""
        guard = bool(n.get("exceptions")) or n.get("time_window", {}).get("status") not in (None, "parsed")
        if n["type"] == "narrative":
            raise _Unsupported(f"{n['computability']}: {n.get('subtype') or 'narrative'}")
        if n["type"] == "predicate":
            e = self._leaf(n)
        else:
            kids = []
            for c in n["children"]:
                kids.append(self._child(c, tag))
            if n["op"] == "NOT":
                e = f"not ({kids[0]})"
            elif n["op"] in ("ALL", "ANY"):
                e = ("\n    " + (" and " if n["op"] == "ALL" else " or ")).join(f"({k})" for k in kids)
            else:
                raise _Unsupported(f"operator {n['op']} not in the tested subset")
        if guard:
            return f"if ({e}) is true then null as Boolean else ({e})"
        return e

    def _child(self, c, tag):
        """a child that is unsupported contributes null (unknown) -- visible, not dropped"""
        try:
            e = self._expr(c, tag)
            self.executable += 1 if c["type"] == "predicate" else 0
            return e
        except _Unsupported as u:
            self.unsupported.append({"criterion": tag, "node": c["id"], "reason": str(u), "text": c["text"][:90]})
            return "null as Boolean /* UNSUPPORTED: " + str(u).replace("\n", " ").replace("*/", "") + " */"

    def compile(self):
        roots = [r for r in self.cer["criteria"]
                 if not r["scope"] or (self.scope and any(self.scope.lower() in s.lower() for s in r["scope"]))]
        if any(r["scope"] for r in self.cer["criteria"]) and self.scope is None and not [r for r in roots]:
            raise ValueError("scope required")
        req_names = []
        for r in roots:
            num = r["display_number"]
            gated = (r["review_status"] != "validated") and not self.allow_draft
            note = f"  // {r['polarity']}; {r['text'][:100].replace('*/', '')}"
            if gated:
                body = "null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */"
                self.unsupported.append({"criterion": num, "node": r["id"], "reason": "not validated (gated)", "text": r["text"][:90]})
                cond = body
            else:
                cond = self._child(r, num)
            req = f"({cond})" if r["polarity"] == "inclusion" else f"not ({cond})"
            self.defs.append(f"define \"Req {num}\":{note}\n  {req}")
            req_names.append(num)
        outcomes = ",\n  ".join(
            f"Tuple {{ criterion: '{n}', outcome: if \"Req {n}\" is null then 'unresolved' else if \"Req {n}\" then 'satisfied' else 'violated' }}"
            for n in req_names)
        banner = ("// DRAFT: includes criteria that are NOT validated. Not for screening use.\n" if self.allow_draft else
                  "// Gated: only dual-approved (validated) criteria are compiled; the rest return null (unresolved).\n")
        lib = f"EligibilityCER_{self.cer['source']['nct_id']}" + (f"_{slug(self.scope)}" if self.scope else "") + ("_DRAFT" if self.allow_draft else "")
        head = [f"{banner}// Source: {self.cer['source']['registry']} {self.cer['source']['nct_id']} (baseline: {self.cer['source']['protocol_baseline']}); "
                f"CER sha256 {self.cer['source']['content_sha256'][:12]}; lifecycle {self.cer['lifecycle']['status']}",
                f"library {lib} version '0.1.0-{'draft' if self.allow_draft else 'gated'}'", "using FHIR version '4.0.1'",
                "include FHIRHelpers version '4.0.1' called FHIRHelpers",
                'codesystem "LOINC": \'http://loinc.org\'', *self.codes.values(), *self.params.values(),
                "context Patient", ""]
        tail = [f"define \"All Requirements Satisfied\":  // ALL over requirement results; null = unresolved\n  "
                + ("\n    and ".join(f"\"Req {n}\"" for n in req_names) or "true"),
                f"define \"Requirement Outcomes\":\n  {{ {outcomes} }}",
                "define \"Any Requirement Violated\":\n  exists (\"Requirement Outcomes\" O where O.outcome = 'violated')"]
        text = "\n".join(head) + "\n\n" + "\n\n".join(self.helper_defs + self.defs + tail) + "\n"
        manifest = {"library": lib, "scope": self.scope, "gated": not self.allow_draft,
                    "criteria": len(roots), "executable_typed_leaves": self.executable,
                    "unsupported": self.unsupported, "parameters": sorted(self.params),
                    "cql_sha256": hashlib.sha256(text.encode()).hexdigest(),
                    "cer_content_sha256": self.cer["source"]["content_sha256"],
                    "translator_validated": False,
                    "pin": "FHIR 4.0.1 / FHIRHelpers 4.0.1 / CQL-to-ELM translator + engine: to be pinned & tested by the site"}
        return text, manifest


def compile_cql(cer, scope=None, allow_draft=False):
    return Compiler(cer, scope, allow_draft).compile()
