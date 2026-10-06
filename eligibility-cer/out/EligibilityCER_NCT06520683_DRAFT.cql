// DRAFT: includes criteria that are NOT validated. Not for screening use.
// Source: ClinicalTrials.gov NCT06520683 (baseline: registry_excerpt); CER sha256 f05717ce38b4; lifecycle draft
library EligibilityCER_NCT06520683_DRAFT version '0.1.0-draft'
using FHIR version '4.0.1'
include FHIRHelpers version '4.0.1' called FHIRHelpers
codesystem "LOINC": 'http://loinc.org'
code "ECOG (89247-1)": '89247-1' from "LOINC" display 'ECOG Performance Status score'
parameter "StudyStartDate" DateTime  // anchor 'study start'; no default
context Patient


define "ECOG latest in window 0":
  Last([Observation: "ECOG (89247-1)"] O
    where O.status.value in {'final', 'amended', 'corrected'}
      and FHIRHelpers.ToDateTime(O.effective as FHIR.dateTime) in Interval["StudyStartDate" - 10 days, "StudyStartDate"]
    sort by FHIRHelpers.ToDateTime(effective as FHIR.dateTime))

define "Req Demo-min-age":  // inclusion; minimumAge: 18 Years
  (AgeInYears() >= 18)

define "Req Demo-max-age":  // inclusion; maximumAge: 80 Years
  (AgeInYears() <= 80)

define "Req Inc-b1":  // inclusion; dMMR and/or MSI-H colorectal carcinoma that undergo surgical resection
  (((null as Boolean /* UNSUPPORTED: biomarker: needs site genomic mapping / molecular matcher with assay & specimen adequacy */)
     or (null as Boolean /* UNSUPPORTED: biomarker: needs site genomic mapping / molecular matcher with assay & specimen adequacy */))
     and (null as Boolean /* UNSUPPORTED: text_dependent: surgical resection performed (procedure) */))

define "Req Inc-b2":  // inclusion; Pathologically confirmed as stage II (T3-4,N0), with at least one of the following risk factors: 1) 
  ((null as Boolean /* UNSUPPORTED: text_dependent: pathologic stage II (T3-4,N0) */)
     and ((null as Boolean /* UNSUPPORTED: condition 'T4 tumour (T4a/T4b)' has no terminology binding / evidence-adequacy policy */)
     or (null as Boolean /* UNSUPPORTED: condition 'vascular invasion' has no terminology binding / evidence-adequacy policy */)
     or (null as Boolean /* UNSUPPORTED: condition 'perineural invasion' has no terminology binding / evidence-adequacy policy */)
     or (null as Boolean /* UNSUPPORTED: condition 'poor differentiation (incl. mucinous, signet-ring)' has no terminology binding / evidence-adequacy policy */)
     or (null as Boolean /* UNSUPPORTED: condition 'pre-operative obstruction and/or perforation' has no terminology binding / evidence-adequacy policy */)))

define "Req Inc-b3":  // inclusion; Perioperative CT/MR/PET-CT find no signs of metastases
  (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Inc-b4":  // inclusion; Eastern Cooperative Oncology Group (ECOG) performance status of 0 or 1 within 10 days prior to study
  (if "ECOG latest in window 0" is null then null
    else FHIRHelpers.ToInteger("ECOG latest in window 0".value as FHIR.integer) in {0, 1})

define "Req Inc-b5":  // inclusion; Aged 18-80
  ((AgeInYears() >= 18)
     and (AgeInYears() <= 80))

define "Req Inc-b6":  // inclusion; No prior medical therapy (chemotherapy, immunotherapy, biologic or targeted therapy) or radiation th
  (not ((null as Boolean /* UNSUPPORTED: condition 'prior medical therapy for current cancer (chemo/immuno/biologic/targeted)' has no terminology binding / evidence-adequacy policy */)
     or (null as Boolean /* UNSUPPORTED: condition 'prior radiation therapy for current cancer' has no terminology binding / evidence-adequacy policy */)))

define "Req Inc-b7":  // inclusion; Adequate organ function
  (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-b1":  // exclusion; Active autoimmune disease that has required systemic treatment in past 2 years
  not (null as Boolean /* UNSUPPORTED: temporal anchor missing/unresolved */)

define "Req Exc-b2":  // exclusion; Positive surgical margin (R1/R2 resection)
  not (null as Boolean /* UNSUPPORTED: condition 'positive surgical margin (R1/R2)' has no terminology binding / evidence-adequacy policy */)

define "Req Exc-b3":  // exclusion; Presence of post-operative complications that may preclude treatment
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-b4":  // exclusion; Active infection requiring systemic therapy
  not (null as Boolean /* UNSUPPORTED: condition 'active infection requiring systemic therapy' has no terminology binding / evidence-adequacy policy */)

define "Req Exc-b5":  // exclusion; Any other malignant disease within the preceding 5 years with the exception of non-melanomatous skin
  not (null as Boolean /* UNSUPPORTED: temporal anchor missing/unresolved */)

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
