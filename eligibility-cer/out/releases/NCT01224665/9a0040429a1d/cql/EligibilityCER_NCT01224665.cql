// Gated: only dual-approved (validated) criteria are compiled; the rest return null (unresolved).
// Source: ClinicalTrials.gov NCT01224665 (baseline: registry_excerpt); CER sha256 e35717329f7f; lifecycle draft
library EligibilityCER_NCT01224665 version '0.1.0-gated'
using FHIR version '4.0.1'
include FHIRHelpers version '4.0.1' called FHIRHelpers
codesystem "LOINC": 'http://loinc.org'
codesystem "SNOMED CT": 'http://snomed.info/sct'
context Patient


define "Req Demo-min-age":  // inclusion; minimumAge: 18 Years
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Demo-max-age":  // inclusion; maximumAge: 120 Years
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Pre-b1.b1":  // inclusion; Histologically confirmed urothelial carcinoma of the bladder
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Pre-b1.b2":  // inclusion; Predominant urothelial carcinoma with any of the following elements allowed:
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Pre-b1.b3":  // inclusion; No visceral or nodal metastatic disease proximal to the common iliac bifurcation by 2-view chest x-r
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Pre-b1.b4":  // inclusion; No intra-operative pelvic lymph node involvement (confirmed by frozen section) at or above the bifur
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Pre-b2.b1":  // inclusion; Zubrod performance status 0-2
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Pre-b2.b2":  // inclusion; ALT and AST ≤ upper limit of normal (ULN)*
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Pre-b2.b3":  // inclusion; Alkaline phosphatase ≤ ULN*
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Pre-b2.b4":  // inclusion; Not pregnant or nursing
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Pre-b2.b5":  // inclusion; Fertile patients must use an effective contraception
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Pre-b2.b6":  // inclusion; No other prior malignancy except adequately treated basal cell or squamous cell skin cancer, in situ
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Pre-b2.b7":  // inclusion; Medically suitable to undergo cystectomy, in the physician's opinion NOTE: *Levels may be ≥ ULN prov
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Pre-b3.b1":  // inclusion; See Disease Characteristics
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Pre-b3.b2":  // inclusion; No prior partial cystectomy for invasive bladder cancer
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Pre-b3.b3":  // inclusion; No prior pelvic surgery that would obviate a complete extended lymphadenectomy (e.g., aorto-femoral/
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Pre-b3.b4":  // inclusion; Prior neoadjuvant chemotherapy for this cancer allowed provided it has been completed and patient ha
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Pre-b3.b5":  // inclusion; No prior pelvic irradiation
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "All Requirements Satisfied":  // ALL over requirement results; null = unresolved
  "Req Demo-min-age"
    and "Req Demo-max-age"
    and "Req Pre-b1.b1"
    and "Req Pre-b1.b2"
    and "Req Pre-b1.b3"
    and "Req Pre-b1.b4"
    and "Req Pre-b2.b1"
    and "Req Pre-b2.b2"
    and "Req Pre-b2.b3"
    and "Req Pre-b2.b4"
    and "Req Pre-b2.b5"
    and "Req Pre-b2.b6"
    and "Req Pre-b2.b7"
    and "Req Pre-b3.b1"
    and "Req Pre-b3.b2"
    and "Req Pre-b3.b3"
    and "Req Pre-b3.b4"
    and "Req Pre-b3.b5"

define "Requirement Outcomes":
  { Tuple { criterion: 'Demo-min-age', outcome: if "Req Demo-min-age" is null then 'unresolved' else if "Req Demo-min-age" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Demo-max-age', outcome: if "Req Demo-max-age" is null then 'unresolved' else if "Req Demo-max-age" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Pre-b1.b1', outcome: if "Req Pre-b1.b1" is null then 'unresolved' else if "Req Pre-b1.b1" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Pre-b1.b2', outcome: if "Req Pre-b1.b2" is null then 'unresolved' else if "Req Pre-b1.b2" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Pre-b1.b3', outcome: if "Req Pre-b1.b3" is null then 'unresolved' else if "Req Pre-b1.b3" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Pre-b1.b4', outcome: if "Req Pre-b1.b4" is null then 'unresolved' else if "Req Pre-b1.b4" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Pre-b2.b1', outcome: if "Req Pre-b2.b1" is null then 'unresolved' else if "Req Pre-b2.b1" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Pre-b2.b2', outcome: if "Req Pre-b2.b2" is null then 'unresolved' else if "Req Pre-b2.b2" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Pre-b2.b3', outcome: if "Req Pre-b2.b3" is null then 'unresolved' else if "Req Pre-b2.b3" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Pre-b2.b4', outcome: if "Req Pre-b2.b4" is null then 'unresolved' else if "Req Pre-b2.b4" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Pre-b2.b5', outcome: if "Req Pre-b2.b5" is null then 'unresolved' else if "Req Pre-b2.b5" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Pre-b2.b6', outcome: if "Req Pre-b2.b6" is null then 'unresolved' else if "Req Pre-b2.b6" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Pre-b2.b7', outcome: if "Req Pre-b2.b7" is null then 'unresolved' else if "Req Pre-b2.b7" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Pre-b3.b1', outcome: if "Req Pre-b3.b1" is null then 'unresolved' else if "Req Pre-b3.b1" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Pre-b3.b2', outcome: if "Req Pre-b3.b2" is null then 'unresolved' else if "Req Pre-b3.b2" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Pre-b3.b3', outcome: if "Req Pre-b3.b3" is null then 'unresolved' else if "Req Pre-b3.b3" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Pre-b3.b4', outcome: if "Req Pre-b3.b4" is null then 'unresolved' else if "Req Pre-b3.b4" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Pre-b3.b5', outcome: if "Req Pre-b3.b5" is null then 'unresolved' else if "Req Pre-b3.b5" then 'satisfied' else 'violated' } }

define "Any Requirement Violated":
  exists ("Requirement Outcomes" O where O.outcome = 'violated')
