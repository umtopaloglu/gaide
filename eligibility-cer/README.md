# Source B pilot — ClinicalTrials.gov → draft CER → terminology → review → CQL / graph

Implements **Source B** of the *Dual-Source Computable Eligibility* reference architecture for
registry trials: ct.gov eligibility text → draft **Canonical Eligibility Representation (CER)** →
structure validation → 3-valued evaluation against synthetic patients → HTML review view.

```
python run.py search "lung cancer" --n 5          # candidate NCT ids   (needs ct.gov access)
python run.py fetch NCT06128837 NCT06357533       # -> data/raw/*.json  (needs ct.gov access)
python run.py build                               # data/raw -> out/*.cer.json + out/*.html (+ evidence/ patients)
python run.py evaluate NCT05512364 evidence/NCT05512364_p2_randomised.json --scope "Randomised trial"
python -m unittest discover -s tests
```
Python ≥3.11, standard library only. Open `out/NCT*.html` to inspect.

Six interventional fixtures are bundled — lung: SCLC `NCT06128837`, NSCLC PD-L1-high `NCT06357533`, EGFR-mutated NSCLC `NCT06838273`;
colorectal: dMMR/MSI-H adjuvant `NCT06520683`, mCRC first-line `NCT04547166`; breast ctDNA `NCT05512364` (phased scopes).
They were pulled through the ClinicalTrials.gov connector (eligibility *text*, not protocol PDFs) — re-run `fetch` to replace them.

## Pipeline
```
ct.gov text ─► rule-based draft (cer/build.py)  ─► + authored proposals (authored/NCT*.json, origin=authored_proposal)
            ─► + review sidecar (review/NCT*.json: clinical + informatics sign-off) ─► lifecycle draft→in_review→validated→released
            ─► CQL (cer/cql.py): gated to validated criteria by default; --allow-draft for translator/engine testing
python run.py review NCT06520683      # worklist, riskiest first
python run.py cql NCT06128837 [--scope "Randomised trial"] [--allow-draft]   # out/*.cql + *.manifest.json
CQL_LIB=<translator jars> ./tools_validate_cql.sh out/EligibilityCER_NCT06128837.cql   # real CQL-to-ELM translator
```
* **Authored proposals** are the architecture's "constrained LLM proposes the tree" step, written in-session by Claude and
  stored as plain JSON. They replace the rule-based node (same id/polarity/scope/source span), stay `needs_review`, and carry
  no clinical authority. Example: NCT06520683 Inc-b2 "at least one of the following risk factors" → `ANY` of five conditions.
* **Review sidecar**: a criterion is `validated` only with approve from *both* roles; the CER is `validated` when all are,
  `released` only with an explicit authorization block. Template: `review/NCT06520683.example.json`.
* **CQL**: supported subset = age, ECOG (LOINC proposal), labs with a LOINC binding (value or ×ULN using the result's own
  reference range). Everything else compiles to `null` with an `UNSUPPORTED` reason and is listed in the manifest. Missing /
  non-final / stale evidence → null. A missing temporal anchor is a *parameter with no default* (never `Now()`).
  Validated here with cql-to-elm 3.29.0 (0 errors, all libraries) and executed in `cql-execution` on synthetic FHIR patients
  (`tests/cql_exec/`): supported leaves agree with `cer/evaluate.py`. The translator bundles FHIRHelpers/model **4.0.0**, so
  validation ran against that pair; pin and re-test your own FHIR 4.0.1 stack. LOINC codes are *proposed_unreviewed*.

## What is implemented
| Architecture requirement | Where |
|---|---|
| Source identity, retrieval time, content hash, baseline = *registry excerpt*, completeness disclosure | `cer/build.py` `source`, `completeness_disclosure` |
| Missing CTRP biomarker object ⇒ biomarker coverage **unknown** | `ctrp_biomarker_contract` |
| Complete criterion inventory; every source line accounted for | `validate()` |
| Typed expression tree: ALL / ANY / NOT / ATLEAST, predicates, polarity per criterion, scope (phase/arm) | `build.py`, `evaluate.py` |
| Leaf computability: `structured_computable` / `text_dependent` / `human_judgment` | `extract.classify` |
| Time windows with anchors; missing anchor flagged; exceptions captured (unparsed) | `extract.time_window/exceptions` |
| Biomarker qualifiers & gaps (assay, specimen, local/central) listed, not invented | `predicate.qualifier_gaps` |
| Terminology: LOINC *proposed_unreviewed* for labs only; everything else `unmapped` | `extract.LABS` |
| Truth ≠ computability ≠ outcome; unknown stays unknown; stale/missing/preliminary evidence → unknown; negative biomarker needs adequacy | `evaluate.py` |
| Draft ≠ executable: dispositions are `DRAFT-PROVISIONAL`, never "eligible" | `evaluate()` |

## Known limitations (by design for this pilot)
* **Parser is rule-based; LLM step is manual.** The rule-based parser types only explicit patterns (colorectal/EGFR studies get
  1–5 typed leaves from it). Authored proposals cover a hand-picked subset of criteria per new study, not every criterion.
* **Flat bullet lists lose nesting** (very common on ct.gov). Guessed groupings are flagged `⚑`, and any *violation*
  resting on such an item is downgraded to *unresolved* (see the breast study: risk-alternative OR groups).
* Exceptions ("except …") and time windows are captured but **not executed**; a criterion that depends on one stays unresolved.
* No arm/cohort logic beyond named scopes; no derived functions (CrCl, lines of therapy); no OMOP/Circe output. Biomarker and condition leaves are not compiled to CQL (need site genomic/terminology mappings).
* Codes marked `proposed_unreviewed` are not clinically reviewed.


## Updated plan (6 Oct 2026: terminology + knowledge-graph review) — what changed here
| Plan requirement | Implementation |
|---|---|
| Source B document | Program decision (7 Oct): the ct.gov eligibility text **is** the Source B document. `source.source_role` says so; the completeness disclosure notes what that text can omit |
| Terminology layer: source phrase → canonical binding, cross-links, execution binding, mapping semantics, value set + frozen expansion, provenance, lifecycle (Table 4) | `cer/terminology.py`, `terminology/seed-bundle.json`; per-predicate `binding`; value sets with SHA-256 frozen expansions |
| Mapping relation explicit (equivalent / inexact / broader / … / no-map); unmapped ≠ negative; outage = technical failure | `RELATIONSHIPS`, `no-map` records, `terminology_unavailable` status |
| Graph-compatible CER: RDF 1.1 / JSON-LD 1.1, ordered operands, release snapshot as named graph, PROV-O, SKOS, SHACL Core, canonical hash, round-trip, competency queries | `cer/graph.py`, `graph/cer-shapes.ttl`, `python run.py graph NCT…` |
| Registry conflict = typed record, never overwrites the CER, blocks release while open | `cer/conflicts.py` (structured age vs narrative), `review.apply_review` |
| Compiler capability manifest: every node supported / conditionally / unsupported; trial-backend label full / partial / unavailable; unsupported ≠ false | `manifest.capability` in `out/*.manifest.json` |
| Missing EHR data must not become a negative via empty retrieval | CQL conditions: `recorded → true; else ConditionCoverageComplete ? false : null` (parameter default **false**); verified in `cql-execution` (`tests/cql_exec/cond.js`) |
| Outcome model: truth / requirement result / applicability / technical status / review status separate; versions on each result | `evaluate()` rows + `versions` |
| Source B fidelity metrics (criterion accounting, predicate P/R/F1 + Wilson 95% CI, critical discrepancies) | `cer/fidelity.py`, `reference/*.example.json` (**not** independent) |
| Don't assume equivalence between performance scales | `performance_status` kind (Zubrod ≠ ECOG) |

**Terminology seed caveat.** No licensed SNOMED CT / UMLS / NCIt / RxNorm access here. The 31 seed concepts (LOINC, SNOMED CT, HGNC) were entered from the
assistant's general knowledge and are `proposed_unreviewed`; NCIt and UMLS CUI fields are intentionally empty; OMOP concept ids are never invented.
Verify every code against the pinned release (terminology lead) before use. SNOMED value sets are *exact-code only* (no descendant expansion), which can lower recall.

**Not yet done:** SHACL Core cannot express NOT-arity (enforced in tests); no OMOP/Circe projection; no native graph store; no UMLS/NCIt lookups;
fidelity numbers need an independently adjudicated reference; PROV-O is modelled for source spans/origin/review but not full activity/agent records.

## LLM proposer (pluggable)
Nothing in the pipeline called an LLM before this; earlier `authored/*.json` trees were written by hand in-session.
`cer/llm/` lets an API model **propose** trees; it can never approve them.

```
python run.py propose NCT04547166 --dry-run                     # show exact prompt + schema; no call
python run.py propose NCT04547166                               # default provider from llm.config.json
python run.py propose NCT04547166 --criteria Exc-4,Exc-5 --provider anthropic --model claude-opus-5-5
python run.py build                                             # proposals/llm/NCT*.json are overlaid as origin=llm_proposal
```
* **Claude** (`anthropic` provider, official SDK): structured output (JSON schema), adaptive thinking, effort `high`,
  server-side refusal fallback `fallbacks: "default"` (set `"fallbacks": null` in `llm.config.json` to turn it off).
  Credentials come only from the environment: `ANTHROPIC_API_KEY` (or an `ant auth login` profile). `pip install anthropic`.
* **Fail-closed validation** (local, deterministic): grammar (NOT = 1 child, no empty groups, required fields per kind),
  every `source_quote` verbatim in the criterion text, every numeric threshold / window present in the text, criterion id echo.
  Any failure → proposal rejected, criterion left as it was. Refusals, timeouts, bad JSON = technical errors, never clinical results.
* Hand-authored proposals win over LLM ones; a proposal is skipped automatically if the criterion text changed since it was made.
* Provenance per criterion: provider/model requested and served, request id, prompt and schema hashes, confidence, uncertainties.
* Only trial text is sent (`patient_data_sent: false`).

**Add another LLM API**: subclass `cer.llm.base.LLMProvider`, implement `complete_json(system, user, schema, schema_name)`
returning a `ProviderResult(data=<dict matching schema>, ...)`, raise `ProviderRefusal` / `ProviderError` on failure, then add
`"my_llm": {"class": "my_package.my_module:MyProvider", "model": "...", ...}` under `providers` in `llm.config.json`
(read keys from environment variables inside your class; anything containing "key"/"token" is excluded from provenance).
`proposals/llm/replay-example.json` is a hand-written example recording (not model output) used by tests.

## Review Desk, amendments, releases
* **Review Desk** (`python run.py workbench` → `out/workbench/review-desk.html`, published as a private claude.ai page):
  every study's criteria, logic, codes and flags; each signed-in reviewer records Approve / Needs change / Reject as
  Clinical or Informatics. Decisions are stored per reviewer (`reviews/<reviewer>/studies/<NCT>`; each person writes only
  their own, everyone reads all), pinned to the criterion text hash. Pull them back with
  `python run.py import-review dump.json` (rows are validated; malformed ones are rejected and listed). The same person
  cannot supply both roles for one criterion.
* **Amendments**: `python run.py snapshot` / `fetch` keep every distinct text in `data/history/<NCT>/`; `python run.py changes NCT…`
  diffs the last two versions criterion by criterion and lists the impact. Approvals of changed text go stale automatically.
* **Releases**: `python run.py release` writes `out/releases/<NCT>/<id>/` (model, graph, gated CQL per scope with capability
  manifest, terminology snapshot, reviews, proposals, source) with per-file SHA-256, a rollback pointer and the reasons it is
  not yet usable; `python run.py verify <dir>` detects any modification. Identical content gives the identical id.
