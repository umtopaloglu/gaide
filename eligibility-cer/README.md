# Source B pilot — ClinicalTrials.gov → draft CER

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

Three fixtures are bundled (SCLC `NCT06128837`, NSCLC PD-L1-high `NCT06357533`, breast ctDNA `NCT05512364`).
They were pulled through the ClinicalTrials.gov connector, not the REST API — re-run `fetch` to replace them.

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
* **Parser is rule-based, not an LLM.** The architecture has a constrained LLM *propose* the tree; that step is the next
  thing to plug in (same node schema). Here only explicit patterns are typed; the rest stays narrative.
* **Flat bullet lists lose nesting** (very common on ct.gov). Guessed groupings are flagged `⚑`, and any *violation*
  resting on such an item is downgraded to *unresolved* (see the breast study: risk-alternative OR groups).
* Exceptions ("except …") and time windows are captured but **not executed**; a criterion that depends on one stays unresolved.
* No arm/cohort logic beyond named scopes; no derived functions (CrCl, lines of therapy); no CQL/ELM or Circe output yet.
* Codes marked `proposed_unreviewed` are not clinically reviewed.
