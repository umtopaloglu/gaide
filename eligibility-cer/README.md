# Source B pilot — ClinicalTrials.gov → draft CER → review → CQL

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
