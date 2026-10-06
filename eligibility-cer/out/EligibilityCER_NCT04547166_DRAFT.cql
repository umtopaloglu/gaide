// DRAFT: includes criteria that are NOT validated. Not for screening use.
// Source: ClinicalTrials.gov NCT04547166 (baseline: registry_excerpt); CER sha256 da810c71d6e1; lifecycle draft
library EligibilityCER_NCT04547166_DRAFT version '0.1.0-draft'
using FHIR version '4.0.1'
include FHIRHelpers version '4.0.1' called FHIRHelpers
codesystem "LOINC": 'http://loinc.org'
codesystem "SNOMED CT": 'http://snomed.info/sct'
code "ECOG (89247-1)": '89247-1' from "LOINC" display 'ECOG Performance Status score'
parameter "FirstDoseDate" DateTime  // anchor 'first dose'; no default
context Patient


define "ECOG latest in window 0":
  Last([Observation: "ECOG (89247-1)"] O
    where O.status.value in {'final', 'amended', 'corrected'}
      and FHIRHelpers.ToDateTime(O.effective as FHIR.dateTime) in Interval["FirstDoseDate" - 7 days, "FirstDoseDate"]
    sort by FHIRHelpers.ToDateTime(effective as FHIR.dateTime))

define "Req Demo-min-age":  // inclusion; minimumAge: 18 Years
  (AgeInYears() >= 18)

define "Req Demo-max-age":  // inclusion; maximumAge: 75 Years
  (AgeInYears() <= 75)

define "Req Inc-1":  // inclusion; Histopathologically confirmed unresectable metastatic/recurrent colorectal adenocarcinoma
  (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Inc-2":  // inclusion; Life expectancy ≥ 12 weeks
  (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Inc-3":  // inclusion; Have not received any previous systemic anti-tumor drug treatment for metastatic colorectal adenocar
  (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Inc-4":  // inclusion; For participants who have previously received neoadjuvant/adjuvant therapy, the time from the last t
  (null as Boolean /* UNSUPPORTED: text_dependent: prior therapy / medication */)

define "Req Inc-5":  // inclusion; With at least one measurable lesion as assessed by the IRRC per RECIST v1.1, and the measurable lesi
  (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Inc-6":  // inclusion; Agree to provide sufficient previously preserved tumor tissue specimens or agree to undergo biopsy t
  (null as Boolean /* UNSUPPORTED: text_dependent: specimen / tissue availability */)

define "Req Inc-7":  // inclusion; Have an ECOG PS score of 0 or 1 within 7 days prior to receiving the first dose of the study drugs
  (if "ECOG latest in window 0" is null then null
    else FHIRHelpers.ToInteger("ECOG latest in window 0".value as FHIR.integer) in {0, 1})

define "Req Inc-8":  // inclusion; Have Adequate major organ functions.
  (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-1":  // exclusion; Have confirmed MSI-H CRC (gene test)
  not (null as Boolean /* UNSUPPORTED: biomarker: needs site genomic mapping / molecular matcher with assay & specimen adequacy */)

define "Req Exc-2":  // exclusion; Subjects with oligometastatic liver disease and presenting the potential for becoming resectable
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-3":  // exclusion; Presence of central nervous system (CNS) or leptomeningeal metastases
  not ((null as Boolean /* UNSUPPORTED: condition 'CNS metastases' has no terminology binding */)
     or (null as Boolean /* UNSUPPORTED: condition 'leptomeningeal metastases' has no terminology binding */))

define "Req Exc-4":  // exclusion; Have received radiotherapy within 6 months prior to the initiation of study treatment, except for pa
  not (null as Boolean /* UNSUPPORTED: text_dependent: prior therapy / medication */)

define "Req Exc-5":  // exclusion; With a history of or current interstitial pneumonia, pneumoconiosis, radiation pneumonitis, drug-rel
  not (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)

define "Req Exc-6":  // exclusion; Have received major surgery within 28 days prior to randomization. A major surgery in this study is 
  not (null as Boolean /* UNSUPPORTED: condition 'major surgery' has no terminology binding */)

define "Req Exc-7":  // exclusion; Previously received intestinal stent implantation, with the stent remaining in place at the screenin
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-8":  // exclusion; Uncontrolled hypertension despite clinical treatment (defined as systolic blood pressure ≥ 150 mmHg 
  not ((null as Boolean /* UNSUPPORTED: no LOINC binding for 'Systolic blood pressure' (terminology unavailable/unbound) */)
     or (null as Boolean /* UNSUPPORTED: no LOINC binding for 'Diastolic blood pressure' (terminology unavailable/unbound) */))

define "Req Exc-9":  // exclusion; With a history of hypertensive crisis or hypertensive encephalopathy
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-10":  // exclusion; With a history of significant/severe hemorrhage within 1 month prior to randomization, or have recei
  not ((null as Boolean /* UNSUPPORTED: condition 'significant/severe hemorrhage' has no terminology binding */)
     or (null as Boolean /* UNSUPPORTED: condition 'blood transfusion' has no terminology binding */))

define "Req Exc-11":  // exclusion; Requiring long-term treatment with daily administration of nonsteroidal anti-inflammatory drugs (NSA
  not (null as Boolean /* UNSUPPORTED: text_dependent: prior therapy / medication */)

define "Req Exc-12":  // exclusion; With evidence showing the presence of meteorism that cannot be attributed to puncture or recent surg
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-13":  // exclusion; Presence of severe, unhealed or split wounds and active ulcers or untreated fractures
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-14":  // exclusion; Presence of any of the following medical conditions within 6 months prior to randomization:
  not (if ((null as Boolean /* UNSUPPORTED: human_judgment: investigator judgement */)
     or (null as Boolean /* UNSUPPORTED: human_judgment: investigator judgement */)
     or (null as Boolean /* UNSUPPORTED: human_judgment: investigator judgement */)
     or (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)) is true then null as Boolean else ((null as Boolean /* UNSUPPORTED: human_judgment: investigator judgement */)
     or (null as Boolean /* UNSUPPORTED: human_judgment: investigator judgement */)
     or (null as Boolean /* UNSUPPORTED: human_judgment: investigator judgement */)
     or (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)))

define "All Requirements Satisfied":  // ALL over requirement results; null = unresolved
  "Req Demo-min-age"
    and "Req Demo-max-age"
    and "Req Inc-1"
    and "Req Inc-2"
    and "Req Inc-3"
    and "Req Inc-4"
    and "Req Inc-5"
    and "Req Inc-6"
    and "Req Inc-7"
    and "Req Inc-8"
    and "Req Exc-1"
    and "Req Exc-2"
    and "Req Exc-3"
    and "Req Exc-4"
    and "Req Exc-5"
    and "Req Exc-6"
    and "Req Exc-7"
    and "Req Exc-8"
    and "Req Exc-9"
    and "Req Exc-10"
    and "Req Exc-11"
    and "Req Exc-12"
    and "Req Exc-13"
    and "Req Exc-14"

define "Requirement Outcomes":
  { Tuple { criterion: 'Demo-min-age', outcome: if "Req Demo-min-age" is null then 'unresolved' else if "Req Demo-min-age" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Demo-max-age', outcome: if "Req Demo-max-age" is null then 'unresolved' else if "Req Demo-max-age" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1', outcome: if "Req Inc-1" is null then 'unresolved' else if "Req Inc-1" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-2', outcome: if "Req Inc-2" is null then 'unresolved' else if "Req Inc-2" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-3', outcome: if "Req Inc-3" is null then 'unresolved' else if "Req Inc-3" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-4', outcome: if "Req Inc-4" is null then 'unresolved' else if "Req Inc-4" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-5', outcome: if "Req Inc-5" is null then 'unresolved' else if "Req Inc-5" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-6', outcome: if "Req Inc-6" is null then 'unresolved' else if "Req Inc-6" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-7', outcome: if "Req Inc-7" is null then 'unresolved' else if "Req Inc-7" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-8', outcome: if "Req Inc-8" is null then 'unresolved' else if "Req Inc-8" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-1', outcome: if "Req Exc-1" is null then 'unresolved' else if "Req Exc-1" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-2', outcome: if "Req Exc-2" is null then 'unresolved' else if "Req Exc-2" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-3', outcome: if "Req Exc-3" is null then 'unresolved' else if "Req Exc-3" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-4', outcome: if "Req Exc-4" is null then 'unresolved' else if "Req Exc-4" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-5', outcome: if "Req Exc-5" is null then 'unresolved' else if "Req Exc-5" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-6', outcome: if "Req Exc-6" is null then 'unresolved' else if "Req Exc-6" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-7', outcome: if "Req Exc-7" is null then 'unresolved' else if "Req Exc-7" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-8', outcome: if "Req Exc-8" is null then 'unresolved' else if "Req Exc-8" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-9', outcome: if "Req Exc-9" is null then 'unresolved' else if "Req Exc-9" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-10', outcome: if "Req Exc-10" is null then 'unresolved' else if "Req Exc-10" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-11', outcome: if "Req Exc-11" is null then 'unresolved' else if "Req Exc-11" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-12', outcome: if "Req Exc-12" is null then 'unresolved' else if "Req Exc-12" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-13', outcome: if "Req Exc-13" is null then 'unresolved' else if "Req Exc-13" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-14', outcome: if "Req Exc-14" is null then 'unresolved' else if "Req Exc-14" then 'satisfied' else 'violated' } }

define "Any Requirement Violated":
  exists ("Requirement Outcomes" O where O.outcome = 'violated')
