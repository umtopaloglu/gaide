// DRAFT: includes criteria that are NOT validated. Not for screening use.
// Source: ClinicalTrials.gov NCT02635009 (baseline: registry_excerpt); CER sha256 5c49cfbd66c1; lifecycle draft
library EligibilityCER_NCT02635009_DRAFT version '0.1.0-draft'
using FHIR version '4.0.1'
include FHIRHelpers version '4.0.1' called FHIRHelpers
codesystem "LOINC": 'http://loinc.org'
codesystem "SNOMED CT": 'http://snomed.info/sct'
code "HIV infection (86406008)": '86406008' from "SNOMED CT" display 'Human immunodeficiency virus infection'
parameter "ConditionCoverageComplete" Boolean default false  // site asserts the Condition record is complete enough that absence = false
context Patient


define "HIV infection recorded":
  exists ([Condition: "HIV infection (86406008)"])

define "Req Demo-min-age":  // inclusion; minimumAge: 18 Years
  (AgeInYears() >= 18)

define "Req Exc-b1":  // exclusion; Prior radiotherapy to the head or neck (except for T1 glottic cancer), resulting in overlap of radia
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-b2":  // exclusion; Radiographic evidence of central nervous system (CNS) metastases
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-b3":  // exclusion; Radiographic evidence of hydrocephalus or other architectural distortion of the ventricular system, 
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-b4":  // exclusion; Planned concurrent chemotherapy during PCI
  not ((null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */))

define "Req Exc-b5":  // exclusion; Concomitant invasive malignancy or invasive malignancy within the past five years other than non-mel
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-b6":  // exclusion; Contraindication to MR imaging, such as implanted metal devices or foreign bodies or severe claustro
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-b7":  // exclusion; Severe, active comorbidity, defined as follows:
  not ((null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)
     and (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)
     and (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)
     and (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)
     and (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)
     and (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)
     and ((null as Boolean /* UNSUPPORTED: text_dependent: prior therapy / medication */)
     and (if "HIV infection recorded" then true else (if "ConditionCoverageComplete" then false else null as Boolean))))

define "Req Exc-b8":  // exclusion; Pregnant or lactating women or women of childbearing potential and male participants who are sexuall
  not (null as Boolean /* UNSUPPORTED: human_judgment: consent / contraception / pregnancy workflow */)

define "All Requirements Satisfied":  // ALL over requirement results; null = unresolved
  "Req Demo-min-age"
    and "Req Exc-b1"
    and "Req Exc-b2"
    and "Req Exc-b3"
    and "Req Exc-b4"
    and "Req Exc-b5"
    and "Req Exc-b6"
    and "Req Exc-b7"
    and "Req Exc-b8"

define "Requirement Outcomes":
  { Tuple { criterion: 'Demo-min-age', outcome: if "Req Demo-min-age" is null then 'unresolved' else if "Req Demo-min-age" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b1', outcome: if "Req Exc-b1" is null then 'unresolved' else if "Req Exc-b1" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b2', outcome: if "Req Exc-b2" is null then 'unresolved' else if "Req Exc-b2" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b3', outcome: if "Req Exc-b3" is null then 'unresolved' else if "Req Exc-b3" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b4', outcome: if "Req Exc-b4" is null then 'unresolved' else if "Req Exc-b4" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b5', outcome: if "Req Exc-b5" is null then 'unresolved' else if "Req Exc-b5" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b6', outcome: if "Req Exc-b6" is null then 'unresolved' else if "Req Exc-b6" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b7', outcome: if "Req Exc-b7" is null then 'unresolved' else if "Req Exc-b7" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-b8', outcome: if "Req Exc-b8" is null then 'unresolved' else if "Req Exc-b8" then 'satisfied' else 'violated' } }

define "Any Requirement Violated":
  exists ("Requirement Outcomes" O where O.outcome = 'violated')
