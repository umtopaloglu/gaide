// DRAFT: includes criteria that are NOT validated. Not for screening use.
// Source: ClinicalTrials.gov NCT05512364 (baseline: registry_excerpt); CER sha256 7f692e2377cc; lifecycle draft
library EligibilityCER_NCT05512364_randomised_trial_DRAFT version '0.1.0-draft'
using FHIR version '4.0.1'
include FHIRHelpers version '4.0.1' called FHIRHelpers
codesystem "LOINC": 'http://loinc.org'
code "ECOG (89247-1)": '89247-1' from "LOINC" display 'ECOG Performance Status score'
parameter "ScreeningDate" DateTime  // no default on purpose: a missing anchor is unknown, not today
parameter "LabMaxAgeDays" Integer default 90  // site evidence-freshness policy
context Patient


define "ECOG latest":
  Last([Observation: "ECOG (89247-1)"] O
    where O.status.value in {'final', 'amended', 'corrected'}
      and days between FHIRHelpers.ToDateTime(O.effective as FHIR.dateTime) and "ScreeningDate" in Interval[0, "LabMaxAgeDays"]
    sort by FHIRHelpers.ToDateTime(effective as FHIR.dateTime))

define "Req Demo-min-age":  // inclusion; minimumAge: 18 Years
  (AgeInYears() >= 18)

define "Req Inc-2.b1.b1":  // inclusion; ctDNA positive according to the Signatera ctDNA assay (main study ctDNA test) or other ctDNA assay a
  ((null as Boolean /* UNSUPPORTED: biomarker: needs site genomic mapping / molecular matcher with assay & specimen adequacy */)
     and (null as Boolean /* UNSUPPORTED: text_dependent: residual text not covered by typed predicates */))

define "Req Inc-2.b1.b2":  // inclusion; Patients must meet the eligibility criteria for the screening phase, with the exception of the tissu
  (null as Boolean /* UNSUPPORTED: text_dependent: specimen / tissue availability */)

define "Req Inc-2.b1.b3":  // inclusion; Patients must receive adjuvant ET at the time of the ctDNA positive test
  (null as Boolean /* UNSUPPORTED: biomarker: needs site genomic mapping / molecular matcher with assay & specimen adequacy */)

define "Req Inc-2.b1.b4":  // inclusion; Absence of locoregional and/or metastatic disease and/or new malignancy, as investigated by:
  (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Inc-2.b1.b5":  // inclusion; Mammogram (unilateral in case of mastectomy; not required in patients having undergone bilateral mas
  (null as Boolean /* UNSUPPORTED: human_judgment: investigator judgement */)

define "Req Inc-2.b1.b6":  // inclusion; CT thorax and abdomen/pelvis with IV contrast. In case of any contra-indications (medical or regulat
  (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Inc-2.b1.b7":  // inclusion; Technetium-99m bone scintigraphy
  (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Inc-2.b1.b8":  // inclusion; Eastern Cooperative Oncology Group (ECOG) performance status (PS) 0-1
  (if "ECOG latest" is null then null
    else FHIRHelpers.ToInteger("ECOG latest".value as FHIR.integer) in {0, 1})

define "Req Inc-2.b1.b9":  // inclusion; Adequate organ function
  (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Inc-2.b1.b10":  // inclusion; Women of childbearing potential (WOCBP) must have a negative highly sensitive serum or urine pregnan
  (null as Boolean /* UNSUPPORTED: human_judgment: consent / contraception / pregnancy workflow */)

define "Req Inc-2.b2.b1":  // exclusion; Any unresolved toxic effect of prior therapies or surgical procedures of Grade ≥ 2 according to Comm
  not (null as Boolean /* UNSUPPORTED: human_judgment: investigator judgement */)

define "Req Inc-2.b2.b2":  // exclusion; Unable or unwilling to avoid over-the-counter medications, dietary/herbal supplements, and/or foods 
  not (null as Boolean /* UNSUPPORTED: human_judgment: consent / contraception / pregnancy workflow */)

define "Req Inc-2.b2.b3":  // exclusion; Known difficulty in tolerating oral medications or conditions which would impair absorption of oral 
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Inc-2.b2.b4":  // exclusion; Any of the following cardiovascular disorders within 3 months before enrolment:
  not (if ((null as Boolean /* UNSUPPORTED: condition 'myocardial infarction' has no terminology binding / evidence-adequacy policy */)
     or (null as Boolean /* UNSUPPORTED: condition 'stroke' has no terminology binding / evidence-adequacy policy */)
     or (null as Boolean /* UNSUPPORTED: condition 'unstable angina' has no terminology binding / evidence-adequacy policy */)
     or (null as Boolean /* UNSUPPORTED: condition 'arrhythmia' has no terminology binding / evidence-adequacy policy */)
     or (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)
     or (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)) is true then null as Boolean else ((null as Boolean /* UNSUPPORTED: condition 'myocardial infarction' has no terminology binding / evidence-adequacy policy */)
     or (null as Boolean /* UNSUPPORTED: condition 'stroke' has no terminology binding / evidence-adequacy policy */)
     or (null as Boolean /* UNSUPPORTED: condition 'unstable angina' has no terminology binding / evidence-adequacy policy */)
     or (null as Boolean /* UNSUPPORTED: condition 'arrhythmia' has no terminology binding / evidence-adequacy policy */)
     or (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)
     or (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)))

define "Req Inc-2.b2.b5":  // exclusion; CTCAE version 5.0 grade 3 or 4 dyslipidemia at the time of screening, defined as cholesterol>400 mg/
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Inc-2.b2.b6":  // exclusion; Child-Pugh Score greater than Class A
  not (null as Boolean /* UNSUPPORTED: condition 'ild' has no terminology binding / evidence-adequacy policy */)

define "Req Inc-2.b2.b7":  // exclusion; Uncontrolled significant active infections (≥ grade 3 according to CTCAE version 5), including activ
  not (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)

define "Req Inc-2.b2.b8":  // exclusion; Coagulopathy or any history of coagulopathy within the past 6 months, including history of deep vein
  not (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)

define "All Requirements Satisfied":  // ALL over requirement results; null = unresolved
  "Req Demo-min-age"
    and "Req Inc-2.b1.b1"
    and "Req Inc-2.b1.b2"
    and "Req Inc-2.b1.b3"
    and "Req Inc-2.b1.b4"
    and "Req Inc-2.b1.b5"
    and "Req Inc-2.b1.b6"
    and "Req Inc-2.b1.b7"
    and "Req Inc-2.b1.b8"
    and "Req Inc-2.b1.b9"
    and "Req Inc-2.b1.b10"
    and "Req Inc-2.b2.b1"
    and "Req Inc-2.b2.b2"
    and "Req Inc-2.b2.b3"
    and "Req Inc-2.b2.b4"
    and "Req Inc-2.b2.b5"
    and "Req Inc-2.b2.b6"
    and "Req Inc-2.b2.b7"
    and "Req Inc-2.b2.b8"

define "Requirement Outcomes":
  { Tuple { criterion: 'Demo-min-age', outcome: if "Req Demo-min-age" is null then 'unresolved' else if "Req Demo-min-age" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-2.b1.b1', outcome: if "Req Inc-2.b1.b1" is null then 'unresolved' else if "Req Inc-2.b1.b1" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-2.b1.b2', outcome: if "Req Inc-2.b1.b2" is null then 'unresolved' else if "Req Inc-2.b1.b2" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-2.b1.b3', outcome: if "Req Inc-2.b1.b3" is null then 'unresolved' else if "Req Inc-2.b1.b3" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-2.b1.b4', outcome: if "Req Inc-2.b1.b4" is null then 'unresolved' else if "Req Inc-2.b1.b4" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-2.b1.b5', outcome: if "Req Inc-2.b1.b5" is null then 'unresolved' else if "Req Inc-2.b1.b5" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-2.b1.b6', outcome: if "Req Inc-2.b1.b6" is null then 'unresolved' else if "Req Inc-2.b1.b6" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-2.b1.b7', outcome: if "Req Inc-2.b1.b7" is null then 'unresolved' else if "Req Inc-2.b1.b7" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-2.b1.b8', outcome: if "Req Inc-2.b1.b8" is null then 'unresolved' else if "Req Inc-2.b1.b8" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-2.b1.b9', outcome: if "Req Inc-2.b1.b9" is null then 'unresolved' else if "Req Inc-2.b1.b9" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-2.b1.b10', outcome: if "Req Inc-2.b1.b10" is null then 'unresolved' else if "Req Inc-2.b1.b10" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-2.b2.b1', outcome: if "Req Inc-2.b2.b1" is null then 'unresolved' else if "Req Inc-2.b2.b1" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-2.b2.b2', outcome: if "Req Inc-2.b2.b2" is null then 'unresolved' else if "Req Inc-2.b2.b2" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-2.b2.b3', outcome: if "Req Inc-2.b2.b3" is null then 'unresolved' else if "Req Inc-2.b2.b3" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-2.b2.b4', outcome: if "Req Inc-2.b2.b4" is null then 'unresolved' else if "Req Inc-2.b2.b4" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-2.b2.b5', outcome: if "Req Inc-2.b2.b5" is null then 'unresolved' else if "Req Inc-2.b2.b5" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-2.b2.b6', outcome: if "Req Inc-2.b2.b6" is null then 'unresolved' else if "Req Inc-2.b2.b6" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-2.b2.b7', outcome: if "Req Inc-2.b2.b7" is null then 'unresolved' else if "Req Inc-2.b2.b7" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-2.b2.b8', outcome: if "Req Inc-2.b2.b8" is null then 'unresolved' else if "Req Inc-2.b2.b8" then 'satisfied' else 'violated' } }

define "Any Requirement Violated":
  exists ("Requirement Outcomes" O where O.outcome = 'violated')
