// Gated: only dual-approved (validated) criteria are compiled; the rest return null (unresolved).
// Source: ClinicalTrials.gov NCT06520683 (baseline: registry_excerpt); CER sha256 f05717ce38b4; lifecycle draft
library EligibilityCER_NCT06520683 version '0.1.0-gated'
using FHIR version '4.0.1'
include FHIRHelpers version '4.0.1' called FHIRHelpers
codesystem "LOINC": 'http://loinc.org'
codesystem "SNOMED CT": 'http://snomed.info/sct'
context Patient


define "Req Demo-min-age":  // inclusion; minimumAge: 18 Years
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Demo-max-age":  // inclusion; maximumAge: 80 Years
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b1":  // inclusion; dMMR and/or MSI-H colorectal carcinoma that undergo surgical resection
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b2":  // inclusion; Pathologically confirmed as stage II (T3-4,N0), with at least one of the following risk factors: 1) 
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b3":  // inclusion; Perioperative CT/MR/PET-CT find no signs of metastases
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b4":  // inclusion; Eastern Cooperative Oncology Group (ECOG) performance status of 0 or 1 within 10 days prior to study
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b5":  // inclusion; Aged 18-80
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b6":  // inclusion; No prior medical therapy (chemotherapy, immunotherapy, biologic or targeted therapy) or radiation th
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b7":  // inclusion; Adequate organ function
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Exc-b1":  // exclusion; Active autoimmune disease that has required systemic treatment in past 2 years
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Exc-b2":  // exclusion; Positive surgical margin (R1/R2 resection)
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Exc-b3":  // exclusion; Presence of post-operative complications that may preclude treatment
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Exc-b4":  // exclusion; Active infection requiring systemic therapy
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Exc-b5":  // exclusion; Any other malignant disease within the preceding 5 years with the exception of non-melanomatous skin
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "All Requirements Satisfied":  // ALL over requirement results; null = unresolved
  "Req Demo-min-age"
    and "Req Demo-max-age"
    and "Req Inc-b1"
    and "Req Inc-b2"
    and "Req Inc-b3"
    and "Req Inc-b4"
    and "Req Inc-b5"
    and "Req Inc-b6"
    and "Req Inc-b7"
    and "Req Exc-b1"
    and "Req Exc-b2"
    and "Req Exc-b3"
    and "Req Exc-b4"
    and "Req Exc-b5"

define "Requirement Outcomes":
  { Tuple { criterion: 'Demo-min-age', outcome: if "Req Demo-min-age" is null then 'unresolved' else if "Req Demo-min-age" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Demo-max-age', outcome: if "Req Demo-max-age" is null then 'unresolved' else if "Req Demo-max-age" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b1', outcome: if "Req Inc-b1" is null then 'unresolved' else if "Req Inc-b1" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b2', outcome: if "Req Inc-b2" is null then 'unresolved' else if "Req Inc-b2" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b3', outcome: if "Req Inc-b3" is null then 'unresolved' else if "Req Inc-b3" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b4', outcome: if "Req Inc-b4" is null then 'unresolved' else if "Req Inc-b4" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b5', outcome: if "Req Inc-b5" is null then 'unresolved' else if "Req Inc-b5" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b6', outcome: if "Req Inc-b6" is null then 'unresolved' else if "Req Inc-b6" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b7', outcome: if "Req Inc-b7" is null then 'unresolved' else if "Req Inc-b7" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b1', outcome: if "Req Exc-b1" is null then 'unresolved' else if "Req Exc-b1" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b2', outcome: if "Req Exc-b2" is null then 'unresolved' else if "Req Exc-b2" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b3', outcome: if "Req Exc-b3" is null then 'unresolved' else if "Req Exc-b3" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b4', outcome: if "Req Exc-b4" is null then 'unresolved' else if "Req Exc-b4" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b5', outcome: if "Req Exc-b5" is null then 'unresolved' else if "Req Exc-b5" then 'satisfied' else 'violated' } }

define "Any Requirement Violated":
  exists ("Requirement Outcomes" O where O.outcome = 'violated')
