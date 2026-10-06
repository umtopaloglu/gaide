"""Rule-based extraction of typed predicates from one criterion's text.

Deliberately narrow: it only emits a typed predicate when the text matches an
explicit pattern.  Everything else stays narrative (text_dependent or
human_judgment) -- never approximated.  Terminology bindings are *proposed*
and unreviewed; unknown concepts are left unmapped rather than invented.
"""
import re

NORM_CMP = {"≥": ">=", "≤": "<=", ">=": ">=", "<=": "<=", "<": "<", ">": ">", "=": "="}

# analyte -> (alias regex, proposed LOINC or None).  Codes are unreviewed proposals.
LABS = {
    "ANC": (r"absolute neutrophil count|neutrophils?(?:\s*count)?|ANC", "751-8"),
    "Platelets": (r"platelets?(?:\s*count)?|PLT", "777-3"),
    "Hemoglobin": (r"hemoglobin|haemoglobin|Hb", "718-7"),
    "Total bilirubin": (r"total bilirubin|TBIL|bilirubin", "1975-2"),
    "AST": (r"aspartate aminotransferase|AST", "1920-8"),
    "ALT": (r"alanine aminotransferase|ALT", "1742-6"),
    "Albumin": (r"serum albumin|albumin", "1751-7"),
    "Creatinine clearance": (r"creatinine clearance|CrCl", "2164-2"),
    "Creatinine": (r"serum creatinine|creatinine", "2160-0"),
    "INR": (r"PT-INR|INR", "6301-6"),
}
MEASURES = {
    "Ki-67": r"Ki-?67",
    "Tumour size": r"tumou?r size",
    "Oncotype DX recurrence score": r"Oncotype Dx Recurrence Score",
    "Prosigna score": r"Prosigna score",
    "EPclin risk score": r"EPclin risk score",
    "Allred proportion score": r"Allred(?: proportion)? score",
    "ER staining (% cells)": r"ER(?=[- ]positive)",
    "Tumour content": r"tumou?r content",
}
_ALIASES = [(n, p, "lab") for n, (p, _) in LABS.items()] + [(n, p, "measurement") for n, p in MEASURES.items()]
_ALIAS_PLAIN = "|".join(rf"(?:\b(?:{p})\b)" for (_, p, _) in _ALIASES)
LAB_RE = re.compile(
    rf"(?P<names>(?:{_ALIAS_PLAIN})(?:\s*\([A-Za-z0-9\-]+\))?(?:\s*(?:,|and|/|or)\s*(?:{_ALIAS_PLAIN})(?:\s*\([A-Za-z0-9\-]+\))?)*)"
    r"(?P<gap>[^≥≤<>=;:]{0,28}?)"
    r"(?P<cmp>≥|≤|>=|<=|<|>)\s*(?P<val>\d+(?:\.\d+)?)"
    r"(?P<tail>\s*[×x]\s*(?:ULN|upper limit of normal(?:\s*\(ULN\))?|10\^?9\s*/\s*L|109/L))?"
    r"(?:\s*(?P<unit>g/dL|g/L|mg/dL|mL/min|mmol/L|µmol/L|μmol/L|mg/L|IU/mL|cm|mm|%))?",
    re.I,
)
_ALIAS_ONE = [(n, re.compile(p, re.I), k) for (n, p, k) in _ALIASES]
_CASE_SENSITIVE = {"ER staining (% cells)"}

AGE_RE = re.compile(r"\bage\s*(?P<cmp>≥|>=|>|≤|<=|<)\s*(?P<val>\d+)\s*(?:years?)?", re.I)
ECOG_RE = re.compile(r"\bECOG\b.{0,70}?(?P<cmp>≤|<=|<|≥|>=|>)?\s*\b(?P<a>[0-5])\b(?:\s*(?:-|–|to|or)\s*(?P<b>[0-5])\b)?", re.I)
PDL1_RE = re.compile(r"PD-?L1.{0,60}?(?:(?P<method>TC|TPS|CPS|TAP|IC)\s*)?(?P<cmp>≥|>=|>|≤|<=|<)\s*(?P<val>\d+)\s*%", re.I)
GENE_LIST = r"(?:EGFR|ALK|ROS1|KRAS|BRAF|HER2|ERBB2|MET|RET|NTRK[123]?|BRCA[12]?)"
GENE_RE = re.compile(rf"(?P<genes>\b{GENE_LIST}\b(?:\s*(?:,|and|or|/)\s*{GENE_LIST}\b)*)\s*(?P<alt>mutations?|rearrangements?|fusions?|amplification|alterations?|positive|negative|overexpression)?", re.I)
ABSENCE_RE = re.compile(r"\b(absence of|absent|no (?:evidence|known)|without|wild[- ]type)\b", re.I)
HR_RE = re.compile(r"\b(?P<g>ER|HER2|PR)[- ](?P<s>positive|negative)\b")
CTDNA_RE = re.compile(r"\bctDNA[- ](?P<s>positive|negative)\b", re.I)
VIRAL_RE = re.compile(r"\b(?P<a>HBsAg|HBV|HCV|HIV|hepatitis [BC](?: virus)?|human immunodeficiency virus)\b", re.I)

TIME_RE = re.compile(
    r"\b(?:within|in|during|for)\s+(?:the\s+)?(?:last\s+|past\s+)?(?P<n>\d+(?:\.\d+)?)\s*(?P<u>day|week|month|year)s?"
    r"(?:\s+(?P<prep>before|prior to|of|from|after|since)\s+(?:the\s+)?(?P<anchor>[A-Za-z ]{3,30}?)(?=[,;.)]|\s*\(|\s+(?:and|or|except)\b|$))?",
    re.I,
)
ANCHORS = ["screening", "randomi[sz]ation", "registration", "enrol(?:l)?ment", "first dose", "consent", "study entry", "baseline"]
EXCEPT_RE = re.compile(r"[\(,;]?\s*\b(?P<kw>except(?: for)?|with the exception of|with exceptions|apart from|other than|unless)\b(?P<body>[^;)]*)\)?", re.I)

JUDGMENT_RE = re.compile(r"\binvestigator|researchers? believe|as determined by|in the opinion|judg|considered unsuitable|not suitable|at the discretion|undesirable", re.I)
CONSENT_RE = re.compile(r"informed consent|contracepti|willing|able to comply|childbearing|pregnan|lactat|WOCBP", re.I)
SPECIMEN_RE = re.compile(r"tumou?r (?:sample|tissue|content)|tissue sample|unstained slides|FFPE|biops(?:y|ies)|archival|must provide", re.I)
THERAPY_RE = re.compile(r"prior (?:systemic )?(?:therapy|treatment)|previous (?:adjuvant )?(?:treatment|therapy)|received .{0,40}(?:therapy|chemotherapy)|treatment with|vaccinated|inhibitors? of|inducers? of", re.I)
CONDITIONS = [
    "hepatitis B", "hepatitis C", "HIV", "myocardial infarction", "unstable angina", "pulmonary embolism",
    "deep vein thrombosis", "stroke", "arrhythmia", "pneumonitis", "interstitial lung disease", "ILD",
    "brain metastas", "leptomeningeal", "spinal cord compression", "autoimmune", "tuberculosis",
    "pleural effusion", "ascites", "coagulopathy", "hypertension", "heart failure", "corneal disease",
    "immunodeficiency", "alcoholism", "hemoptysis", "superior vena cava syndrome", "transplant",
]
COND_RE = re.compile("|".join(re.escape(c) for c in CONDITIONS), re.I)


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def _lab_names(names: str):
    out = []
    for n, rx, kind in _ALIAS_ONE:
        flags = 0 if n in _CASE_SENSITIVE else re.I
        pat = re.compile(rf"\b(?:{rx.pattern})\b", flags)
        if pat.search(names):
            out.append((n, kind))
    # keep creatinine clearance over plain creatinine when both match the same words
    if any(n == "Creatinine clearance" for n, _ in out) and re.search(r"clearance|CrCl", names, re.I):
        out = [(n, k) for n, k in out if n != "Creatinine"]
    # two distinct lab words joined by a connector ("AST and ALT"), keep both
    return out


def extract_predicates(text: str):
    """Return (predicates, connector, spans) where each predicate carries `span`
    (offsets inside `text`) and `key` (evidence lookup key)."""
    preds, spans = [], []

    for m in LAB_RE.finditer(text):
        tail = (m.group("tail") or "").lower()
        unit = m.group("unit")
        uln = None
        if "109" in tail or "10^9" in tail or "10 9" in tail:
            unit = "10*9/L"
        elif tail:
            uln = float(m.group("val"))
        names = _lab_names(m.group("names"))
        if not names:
            continue
        # conditional applicability: "if liver metastases, AST and ALT <= 3 x ULN"
        pre = text[max(0, m.start() - 80): m.start()].split(";")[-1]
        cm = re.search(r"\bif\s+(?P<c>[^,;]+),\s*$", pre, re.I)
        for name, kind in names:
            p = {
                "kind": kind,
                "analyte": name,
                "comparator": NORM_CMP[m.group("cmp")],
                "value": float(m.group("val")),
                "unit": "x ULN" if uln is not None else unit,
                "uln_multiple": uln is not None,
                "key": f"{kind}:{slug(name)}",
                "span": [m.start(), m.end()],
                "terminology": ({"system": "LOINC", "code": LABS[name][1], "status": "proposed_unreviewed"}
                                if name in LABS else {"status": "unmapped"}),
            }
            if cm:
                p["applicability"] = {"status": "unresolved", "condition": cm.group("c").strip(),
                                      "key": "fact:" + slug(cm.group("c"))}
            preds.append(p)
        spans.append((m.start(), m.end()))

    am = AGE_RE.search(text)
    if am:
        preds.append({"kind": "age", "comparator": NORM_CMP[am.group("cmp")], "value": float(am.group("val")),
                      "unit": "a", "key": "age", "span": [am.start(), am.end()],
                      "terminology": {"status": "n/a"}})
        spans.append(am.span())

    em = ECOG_RE.search(text)
    if em:
        a, b, c = int(em.group("a")), em.group("b"), em.group("cmp")
        if c and not b:
            allowed = [v for v in range(0, 6) if {"<": v < a, "<=": v <= a, "≤": v <= a, ">": v > a, ">=": v >= a, "≥": v >= a}[c]]
        elif b:
            lo, hi = a, int(b)
            sep = text[em.end("a"): em.start("b")]
            allowed = list(range(lo, hi + 1)) if re.search(r"-|–|to", sep) else [lo, hi]
        else:
            allowed = [a]
        preds.append({"kind": "ecog", "allowed_values": allowed, "key": "ecog", "span": list(em.span()),
                      "scale": "ECOG", "terminology": {"status": "n/a"}})
        spans.append(em.span())

    pm = PDL1_RE.search(text)
    if pm:
        preds.append({"kind": "biomarker", "analyte": "PD-L1", "alteration": "expression",
                      "required_state": "score", "score_method": (pm.group("method") or "unspecified").upper(),
                      "comparator": NORM_CMP[pm.group("cmp")], "value": float(pm.group("val")), "unit": "%",
                      "key": "biomarker:pd_l1", "span": list(pm.span()), "terminology": {"status": "unmapped"},
                      "qualifier_gaps": ["assay/antibody clone", "specimen/tumour context", "local vs central"]})
        spans.append(pm.span())

    for gm in GENE_RE.finditer(text):
        genes = re.findall(GENE_LIST, gm.group("genes"), re.I)
        alt = (gm.group("alt") or "").lower().rstrip("s")
        clause_start = max(text.rfind(";", 0, gm.start()), text.rfind(".", 0, gm.start()))
        clause = text[clause_start + 1: gm.end()]
        state = "absent" if (ABSENCE_RE.search(clause) or alt == "negative") else "present"
        # `ER`/`HER2` handled by HR_RE below to avoid double counting
        for g in genes:
            if g.upper() == "HER2":
                continue
            preds.append({"kind": "biomarker", "analyte": g.upper(), "alteration": alt or "alteration",
                          "required_state": state, "key": f"biomarker:{g.lower()}",
                          "span": list(gm.span()), "terminology": {"status": "unmapped"},
                          "qualifier_gaps": ["assay", "specimen/tumour context", "local vs central", "variant class detail"]})
        if any(g.upper() != "HER2" for g in genes):
            spans.append(gm.span())

    for hm in HR_RE.finditer(text):
        g = hm.group("g")
        if g == "ER" and any(p.get("analyte") == "ER staining (% cells)" for p in preds):
            continue
        preds.append({"kind": "biomarker", "analyte": g, "alteration": "receptor status",
                      "required_state": "present" if hm.group("s") == "positive" else "absent",
                      "key": f"biomarker:{g.lower()}", "span": list(hm.span()),
                      "terminology": {"status": "unmapped"},
                      "qualifier_gaps": ["assay/scoring method", "specimen", "local vs central"]})
        spans.append(hm.span())

    cm = CTDNA_RE.search(text)
    if cm:
        preds.append({"kind": "biomarker", "analyte": "ctDNA", "alteration": "detection",
                      "required_state": "present" if cm.group("s").lower() == "positive" else "absent",
                      "key": "biomarker:ctdna", "span": list(cm.span()), "terminology": {"status": "unmapped"},
                      "qualifier_gaps": ["assay (protocol names Signatera)", "sampling time"]})
        spans.append(cm.span())

    preds.sort(key=lambda p: p["span"][0])
    connector = "ALL"
    if len(preds) > 1:
        lo, hi = preds[0]["span"][0], preds[-1]["span"][1]
        between = text[lo:hi]
        if re.search(r"\bor\b", between, re.I) and not re.search(r"\band\b(?!/or)", between, re.I):
            connector = "ANY"
        elif re.search(r"\bor\b", between, re.I):
            connector = "MIXED"
    return preds, connector, spans


def time_window(text: str):
    m = TIME_RE.search(text)
    if not m:
        return None
    anchor = (m.group("anchor") or "").strip().lower()
    canon = next((a.replace("(?:l)?", "l").replace("[sz]", "s") for a in ANCHORS if re.search(a, anchor)), None)
    return {"value": float(m.group("n")), "unit": m.group("u").lower(), "direction": "forward" if (m.group("prep") or "").lower() in ("after", "since", "from") else "lookback",
            "anchor": canon or ("unspecified" if not anchor else anchor), "anchor_text": anchor or None,
            "span": list(m.span()), "status": "parsed" if canon else "anchor_missing_or_unrecognised"}


def exceptions(text: str):
    out = []
    for m in EXCEPT_RE.finditer(text):
        out.append({"keyword": m.group("kw").lower(), "text": m.group("body").strip(" ,.)"),
                    "span": list(m.span()), "status": "unparsed"})
    return out


def classify(text: str, has_structured: bool):
    """computability: structured_computable | text_dependent | human_judgment"""
    if has_structured:
        return "structured_computable", None
    if JUDGMENT_RE.search(text):
        return "human_judgment", "investigator judgement"
    if CONSENT_RE.search(text):
        return "human_judgment", "consent / contraception / pregnancy workflow"
    if SPECIMEN_RE.search(text):
        return "text_dependent", "specimen / tissue availability"
    if THERAPY_RE.search(text):
        return "text_dependent", "prior therapy / medication"
    if COND_RE.search(text):
        return "text_dependent", "clinical condition (terminology unbound)"
    return "text_dependent", "unclassified narrative"


def simple_condition(text: str):
    """A short, unqualified condition statement may be typed as a condition predicate."""
    words = text.split()
    if len(words) > 12 or re.search(r",|\bor\b|\band\b", text, re.I) or EXCEPT_RE.search(text) or JUDGMENT_RE.search(text) or TIME_RE.search(text):
        return None
    hits = {m.group(0).lower() for m in COND_RE.finditer(text)}
    if len(hits) != 1:
        return None
    c = hits.pop()
    return {"kind": "condition", "concept": c, "key": f"condition:{slug(c)}", "span": [0, len(text)],
            "terminology": {"status": "unmapped"}}


_STOP = set("the and for with that this any all are was were has have had not who whom from into than then them they their there these those been being will would should may might must can could patients patient subjects subject participants participant male female years year".split())


def uncovered_words(text: str, spans):
    keep = [True] * len(text)
    for a, b in spans:
        for i in range(a, min(b, len(text))):
            keep[i] = False
    rest = "".join(c if k else " " for c, k in zip(text, keep))
    if ":" in rest[:40]:                       # a short "Label:" lead-in is not a requirement
        rest = rest.split(":", 1)[1]
    rest = re.sub(r"Eastern Cooperative Oncology Group|performance status|Oncology|\bPS\b", " ", rest, flags=re.I)
    return [w for w in re.findall(r"[A-Za-z]{3,}", rest) if w.lower() not in _STOP]
