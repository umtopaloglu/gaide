// Gated: only dual-approved (validated) criteria are compiled; the rest return null (unresolved).
// Source: ClinicalTrials.gov NCT06357533 (baseline: registry_excerpt); CER sha256 e9341b774e5c; lifecycle draft
library EligibilityCER_NCT06357533 version '0.1.0-gated'
using FHIR version '4.0.1'
include FHIRHelpers version '4.0.1' called FHIRHelpers
codesystem "LOINC": 'http://loinc.org'
context Patient


define "Req Demo-min-age":  // inclusion; minimumAge: 18 Years
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b1":  // inclusion; Histologically or cytologically documented non-squamous NSCLC.
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b2":  // inclusion; Stage IIIB or IIIC or Stage IV metastatic NSCLC (according to Edition 8 of the AJCC staging manual) 
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b3":  // inclusion; Absence of sensitising EGFR mutations, and ALK and ROS1 rearrangements, and absence of documented lo
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b4":  // inclusion; Must provide tumor sample to determine PD-L1 status, TROP2 status and other biomarkers.
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b5":  // inclusion; Known tumour PD-L1 expression status defined as TC ≥ 50%
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b6":  // inclusion; At least one lesion, not previously irradiated that qualifies as a RECIST 1.1 target lesion at basel
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b7":  // inclusion; ECOG performance status of 0 or 1
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b8":  // inclusion; Adequate bone marrow reserve and organ function
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Exc-b1":  // exclusion; Prior systemic therapy for advanced/metastatic NSCLC.
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Exc-b2":  // exclusion; Squamous cell histology, or predominantly squamous cell histology NSCLC; mixed small cell lung cance
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Exc-b3":  // exclusion; History of another primary malignancy within 3 years
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Exc-b4":  // exclusion; Active or prior documented autoimmune or inflammatory disorders (with exceptions)
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Exc-b5":  // exclusion; Any evidence of severe or uncontrolled disease that makes it undesirable for the participant to part
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Exc-b6":  // exclusion; Has clinically significant third-space fluid retention (for example pleural effusion) and is not ame
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Exc-b7":  // exclusion; History of any ILD/pneumonitis, including radiation pneumonitis (apart from radiation pneumonitis th
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Exc-b8":  // exclusion; Has significant pulmonary function compromise, as determined by the investigator
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Exc-b9":  // exclusion; Spinal cord compression, or brain metastases unless participant treated and no longer symptomatic, r
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Exc-b10":  // exclusion; History of leptomeningeal carcinomatosis
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Exc-b11":  // exclusion; Known clinically significant corneal disease
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Exc-b12":  // exclusion; Active infection with TB, HBV, HCV, Hepatitis A, or known HIV infection that is not well controlled
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Exc-b13":  // exclusion; History of active primary immunodeficiency
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "All Requirements Satisfied":  // ALL over requirement results; null = unresolved
  "Req Demo-min-age"
    and "Req Inc-b1"
    and "Req Inc-b2"
    and "Req Inc-b3"
    and "Req Inc-b4"
    and "Req Inc-b5"
    and "Req Inc-b6"
    and "Req Inc-b7"
    and "Req Inc-b8"
    and "Req Exc-b1"
    and "Req Exc-b2"
    and "Req Exc-b3"
    and "Req Exc-b4"
    and "Req Exc-b5"
    and "Req Exc-b6"
    and "Req Exc-b7"
    and "Req Exc-b8"
    and "Req Exc-b9"
    and "Req Exc-b10"
    and "Req Exc-b11"
    and "Req Exc-b12"
    and "Req Exc-b13"

define "Requirement Outcomes":
  { Tuple { criterion: 'Demo-min-age', outcome: if "Req Demo-min-age" is null then 'unresolved' else if "Req Demo-min-age" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b1', outcome: if "Req Inc-b1" is null then 'unresolved' else if "Req Inc-b1" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b2', outcome: if "Req Inc-b2" is null then 'unresolved' else if "Req Inc-b2" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b3', outcome: if "Req Inc-b3" is null then 'unresolved' else if "Req Inc-b3" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b4', outcome: if "Req Inc-b4" is null then 'unresolved' else if "Req Inc-b4" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b5', outcome: if "Req Inc-b5" is null then 'unresolved' else if "Req Inc-b5" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b6', outcome: if "Req Inc-b6" is null then 'unresolved' else if "Req Inc-b6" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b7', outcome: if "Req Inc-b7" is null then 'unresolved' else if "Req Inc-b7" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b8', outcome: if "Req Inc-b8" is null then 'unresolved' else if "Req Inc-b8" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b1', outcome: if "Req Exc-b1" is null then 'unresolved' else if "Req Exc-b1" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b2', outcome: if "Req Exc-b2" is null then 'unresolved' else if "Req Exc-b2" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b3', outcome: if "Req Exc-b3" is null then 'unresolved' else if "Req Exc-b3" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b4', outcome: if "Req Exc-b4" is null then 'unresolved' else if "Req Exc-b4" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b5', outcome: if "Req Exc-b5" is null then 'unresolved' else if "Req Exc-b5" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b6', outcome: if "Req Exc-b6" is null then 'unresolved' else if "Req Exc-b6" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b7', outcome: if "Req Exc-b7" is null then 'unresolved' else if "Req Exc-b7" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b8', outcome: if "Req Exc-b8" is null then 'unresolved' else if "Req Exc-b8" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b9', outcome: if "Req Exc-b9" is null then 'unresolved' else if "Req Exc-b9" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b10', outcome: if "Req Exc-b10" is null then 'unresolved' else if "Req Exc-b10" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b11', outcome: if "Req Exc-b11" is null then 'unresolved' else if "Req Exc-b11" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b12', outcome: if "Req Exc-b12" is null then 'unresolved' else if "Req Exc-b12" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b13', outcome: if "Req Exc-b13" is null then 'unresolved' else if "Req Exc-b13" then 'satisfied' else 'violated' } }

define "Any Requirement Violated":
  exists ("Requirement Outcomes" O where O.outcome = 'violated')
