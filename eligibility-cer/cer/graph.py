"""Normative graph exchange profile: RDF 1.1 dataset serialised as JSON-LD 1.1 (plan section 4).

* stable HTTPS identifiers (placeholder base -- the program must assign the real URI policy)
* ordered operands are RDF Collections (explicit order), never flattened triples
* one immutable release snapshot = one named graph, with a canonical hash
* PROV-O provenance, SKOS mapping relations, SHACL Core shapes (graph/cer-shapes.ttl)
* lossless round trip:  CER  ->  JSON-LD  ->  CER  (every field, incl. flags/extras via cer:extra JSON literal)
* no patient nodes, ever.
"""
import hashlib
import json
from decimal import Decimal
import os
from datetime import datetime

from rdflib import BNode, Dataset, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.compare import to_canonical_graph
from rdflib.namespace import PROV, RDF, SKOS, XSD

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://cer.example.org/"        # PLACEHOLDER: URI policy is a Phase-1 decision
CER = Namespace(BASE + "vocab#")
SHAPES = os.path.join(HERE, "graph", "cer-shapes.ttl")
SKOS_REL = {"equivalent": SKOS.exactMatch, "inexact": SKOS.closeMatch, "broader": SKOS.broadMatch,
            "narrower": SKOS.narrowMatch, "related": SKOS.relatedMatch}
# scalar node keys modelled explicitly; everything else rides in cer:extra
NODE_SCALARS = {"type": CER.nodeType, "op": CER.operator, "n": CER.count, "text": CER.sourceText, "path": CER.path,
                "polarity": CER.polarity, "polarity_source": CER.polarityBasis, "display_number": CER.displayNumber,
                "computability": CER.computability, "subtype": CER.subtype, "review_status": CER.reviewStatus,
                "origin": CER.origin, "logic_basis": CER.logicBasis, "branch_hint": CER.branchHint,
                "lead_in": CER.leadIn, "supersedes_origin": CER.supersedesOrigin}
MODELLED = set(NODE_SCALARS) | {"id", "children", "source_span", "scope", "predicate", "time_window", "exceptions",
                                "applicability", "binding", "flags", "review", "sub_span"}


def jl(o):
    return Literal(json.dumps(o, sort_keys=True, ensure_ascii=False), datatype=RDF.JSON)


def unjl(l):
    return json.loads(str(l))


def release_id(cer):
    h = hashlib.sha256(json.dumps(cer, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()
    return h


def node_uri(nct, rel, nid):
    return URIRef(f"{BASE}trial/{nct}/release/{rel[:12]}/node/{nid}")


def _emit_node(g, n, nct, rel, order=None):
    u = node_uri(nct, rel, n["id"])
    g.add((u, RDF.type, CER.ExpressionNode))
    g.add((u, CER.identifier, Literal(n["id"])))
    for k, prop in NODE_SCALARS.items():
        if k in n and n[k] is not None:
            v = n[k]
            g.add((u, prop, Literal(v, datatype=XSD.integer) if isinstance(v, int) and not isinstance(v, bool) else Literal(v)))
    # source fidelity: span node derived from the source document (PROV-O)
    sp = BNode()
    g.add((u, PROV.wasDerivedFrom, sp))
    g.add((sp, RDF.type, CER.SourceSpan))
    g.add((sp, CER.start, Literal(n["source_span"][0], datatype=XSD.integer)))
    g.add((sp, CER.end, Literal(n["source_span"][1], datatype=XSD.integer)))
    g.add((u, PROV.wasGeneratedBy, Literal(n.get("origin", "unknown"))))
    if "scope" in n:
        Collection(g, (head := BNode()), [Literal(s) for s in n["scope"]]) if n["scope"] else None
        g.add((u, CER.scope, head if n["scope"] else RDF.nil))
    if "sub_span" in n:
        g.add((u, CER.subSpan, jl(n["sub_span"])))
    if "predicate" in n:
        p = n["predicate"]
        pn = BNode()
        g.add((u, CER.predicate, pn))
        g.add((pn, RDF.type, CER.Predicate))
        g.add((pn, CER.kind, Literal(p["kind"])))
        for k, v in p.items():                                   # typed, queryable predicate fields
            if k == "kind":
                continue
            g.add((pn, CER["p_" + k], jl(v) if (v is None or isinstance(v, (dict, list))) else
                   (Literal(v, datatype=XSD.decimal) if isinstance(v, float) else Literal(v))))
    for key, cls, prop in (("time_window", CER.TemporalConstraint, CER.temporalConstraint),
                           ("applicability", CER.Applicability, CER.applicability)):
        if key in n:
            b = BNode(); g.add((u, prop, b)); g.add((b, RDF.type, cls)); g.add((b, CER.value, jl(n[key])))
            for k, v in n[key].items():
                if k in ("anchor", "unit", "direction", "status", "condition", "key"):
                    g.add((b, CER["t_" + k], Literal(v)))
    if "exceptions" in n:
        head = BNode()
        items = []
        for e in n["exceptions"]:
            b = BNode(); g.add((b, RDF.type, CER.Exception)); g.add((b, CER.value, jl(e))); items.append(b)
        Collection(g, head, items)
        g.add((u, CER.exceptions, head if items else RDF.nil))
    if n.get("binding") is not None:
        bnode = BNode()
        g.add((u, CER.mappingAssertion, bnode))
        b = n["binding"]
        g.add((bnode, RDF.type, CER.MappingAssertion))
        g.add((bnode, CER.value, jl(b)))
        g.add((bnode, CER.relationship, Literal(b["mapping_semantics"]["relationship"])))
        cb = b.get("canonical_binding")
        if cb:
            tgt = URIRef(f"{cb['code_system_uri']}#{cb['primary']['code']}") if cb["code_system_uri"] else None
            g.add((bnode, CER.targetCode, Literal(cb["primary"]["code"])))
            g.add((bnode, CER.targetSystem, Literal(cb["primary"]["system"])))
            rel_p = SKOS_REL.get(b["mapping_semantics"]["relationship"])
            if tgt and rel_p:
                g.add((u, rel_p, tgt))
        if b.get("value_set"):
            g.add((bnode, CER.valueSet, URIRef(f"{BASE}valueset/{b['value_set']['id']}/{b['value_set']['frozen_expansion']['sha256'][:12]}")))
    if n.get("review"):
        for role, d in n["review"].items():
            rn = BNode(); g.add((u, CER.review, rn)); g.add((rn, RDF.type, CER.ReviewDecision)); g.add((rn, CER.role, Literal(role)))
            g.add((rn, CER.value, jl(d)))
    g.add((u, CER.flags, jl(n.get("flags", []))))
    extra = {k: v for k, v in n.items() if k not in MODELLED or (k in ("review", "binding") and not v)}
    if extra:
        g.add((u, CER.extra, jl(extra)))
    if n.get("children") is not None and n["type"] == "group":
        kids = [_emit_node(g, c, nct, rel) for c in n["children"]]
        head = BNode()
        Collection(g, head, kids)
        g.add((u, CER.operand, head))                              # explicit ordered operands
    return u


def to_dataset(cer):
    rel = release_id(cer)
    nct = cer["source"]["nct_id"]
    ds = Dataset()
    gid = URIRef(f"{BASE}trial/{nct}/release/{rel[:12]}")
    g = ds.graph(gid)
    g.add((gid, RDF.type, CER.Release))
    g.add((gid, CER.contentHash, Literal(rel)))
    g.add((gid, CER.lifecycleStatus, Literal(cer["lifecycle"]["status"])))
    g.add((gid, CER.trial, URIRef(f"{BASE}trial/{nct}")))
    doc = URIRef(f"{BASE}trial/{nct}/source/{cer['source']['content_sha256'][:12]}")
    g.add((gid, PROV.wasDerivedFrom, doc))
    g.add((doc, RDF.type, CER.SourceDocument))
    g.add((doc, CER.sha256, Literal(cer["source"]["content_sha256"])))
    g.add((doc, CER.baseline, Literal(cer["source"]["protocol_baseline"])))
    g.add((gid, CER.header, jl({k: v for k, v in cer.items() if k not in ("criteria",)})))
    roots = []
    for r in cer["criteria"]:
        u = _emit_node(g, r, nct, rel)
        g.add((u, RDF.type, CER.Criterion))
        roots.append(u)
    head = BNode()
    Collection(g, head, roots)
    g.add((gid, CER.criteria, head))
    for r in cer["criteria"]:
        g.add((gid, CER.contains, node_uri(nct, rel, r["id"])))
    return ds, gid


def canonical_hash(ds, gid):
    cg = to_canonical_graph(ds.graph(gid))
    lines = sorted(f"{s.n3()} {p.n3()} {o.n3()} ." for s, p, o in cg)
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


CONTEXT = {"cer": str(CER), "prov": str(PROV), "skos": str(SKOS), "xsd": str(XSD)}


def to_jsonld(cer):
    ds, gid = to_dataset(cer)
    txt = ds.serialize(format="json-ld", context=CONTEXT, indent=1)
    return txt, canonical_hash(ds, gid), gid


def _scal(g, u, p):
    v = g.value(u, p)
    return None if v is None else v.toPython()


def _read_node(g, u):
    n = {}
    n["id"] = _scal(g, u, CER.identifier)
    for k, prop in NODE_SCALARS.items():
        v = _scal(g, u, prop)
        if v is not None:
            n[k] = v
    sp = g.value(u, PROV.wasDerivedFrom)
    n["source_span"] = [_scal(g, sp, CER.start), _scal(g, sp, CER.end)]
    sc = g.value(u, CER.scope)
    if sc is not None:
        n["scope"] = [x.toPython() for x in Collection(g, sc)] if sc != RDF.nil else []
    ss = g.value(u, CER.subSpan)
    if ss is not None:
        n["sub_span"] = unjl(ss)
    pn = g.value(u, CER.predicate)
    if pn is not None:
        p = {}
        for _, pp, o in g.triples((pn, None, None)):
            name = str(pp)
            if name.endswith("#kind"):
                p["kind"] = str(o)
            elif "#p_" in name:
                key = name.split("#p_", 1)[1]
                v = unjl(o) if (isinstance(o, Literal) and o.datatype == RDF.JSON) else o.toPython()
                p[key] = float(v) if isinstance(v, Decimal) else v
        n["predicate"] = p
    for key, prop in (("time_window", CER.temporalConstraint), ("applicability", CER.applicability)):
        b = g.value(u, prop)
        if b is not None:
            n[key] = unjl(g.value(b, CER.value))
    ex = g.value(u, CER.exceptions)
    if ex is not None:
        n["exceptions"] = [unjl(g.value(b, CER.value)) for b in Collection(g, ex)] if ex != RDF.nil else []
    ma = g.value(u, CER.mappingAssertion)
    if ma is not None:
        n["binding"] = unjl(g.value(ma, CER.value))
    elif "predicate" in n and False:
        pass
    revs = list(g.objects(u, CER.review))
    if revs:
        n["review"] = {str(g.value(r, CER.role)): unjl(g.value(r, CER.value)) for r in revs}
    n["flags"] = unjl(g.value(u, CER.flags))
    ext = g.value(u, CER.extra)
    if ext is not None:
        n.update(unjl(ext))
    opnd = g.value(u, CER.operand)
    if n.get("type") == "group":
        n["children"] = [_read_node(g, k) for k in Collection(g, opnd)] if opnd is not None else []
    return n


def from_jsonld(text):
    ds = Dataset()
    ds.parse(data=text, format="json-ld")
    gid = next(s for g in ds.graphs() for s in g.subjects(RDF.type, CER.Release))
    g = next(gg for gg in ds.graphs() if (gid, RDF.type, CER.Release) in gg)
    cer = unjl(g.value(gid, CER.header))
    cer["criteria"] = [_read_node(g, k) for k in Collection(g, g.value(gid, CER.criteria))]
    return cer


def validate_shacl(text_or_dataset, gid=None):
    """SHACL Core validation of one release graph.  Returns (conforms, report_text)."""
    from pyshacl import validate
    from rdflib import Graph
    if isinstance(text_or_dataset, str):
        ds = Dataset(); ds.parse(data=text_or_dataset, format="json-ld")
        g = next(gg for gg in ds.graphs() if any(gg.subjects(RDF.type, CER.Release)))
    else:
        g = text_or_dataset.graph(gid)
    flat = Graph()
    for t in g:
        flat.add(t)
    sh = Graph().parse(SHAPES, format="turtle")
    conforms, _, rep = validate(flat, shacl_graph=sh, inference="none", abort_on_first=False)
    return conforms, rep


COMPETENCY = {
 "operands_in_order": """PREFIX cer:<%(c)s> PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
   SELECT ?pos ?kid WHERE { ?g cer:identifier ?gid ; cer:operand/rdf:rest*/rdf:first ?kid . } LIMIT 5""",
 "criteria_by_polarity": """PREFIX cer:<%(c)s> SELECT ?pol (COUNT(?c) AS ?n) WHERE { ?c a cer:Criterion ; cer:polarity ?pol } GROUP BY ?pol""",
 "criteria_using_value_set": """PREFIX cer:<%(c)s> SELECT ?n ?vs WHERE { ?n cer:mappingAssertion ?m . ?m cer:valueSet ?vs }""",
 "unmapped_predicates": """PREFIX cer:<%(c)s> SELECT ?n WHERE { ?n cer:predicate ?p ; cer:mappingAssertion ?m . ?m cer:relationship "no-map" }""",
 "provenance_of_node": """PREFIX cer:<%(c)s> PREFIX prov:<http://www.w3.org/ns/prov#>
   SELECT ?disp ?start ?end ?origin WHERE { ?n cer:displayNumber ?disp ; prov:wasDerivedFrom ?s ; prov:wasGeneratedBy ?origin . ?s cer:start ?start ; cer:end ?end } LIMIT 5""",
}


def competency(ds, gid, name):
    q = COMPETENCY[name] % {"c": str(CER)}
    return list(ds.graph(gid).query(q))
