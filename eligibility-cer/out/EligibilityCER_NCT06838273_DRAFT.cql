// DRAFT: includes criteria that are NOT validated. Not for screening use.
// Source: ClinicalTrials.gov NCT06838273 (baseline: registry_excerpt); CER sha256 6b43ff31aca3; lifecycle draft
library EligibilityCER_NCT06838273_DRAFT version '0.1.0-draft'
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

define "Req Inc-1":  // inclusion; Sign the informed consent form voluntarily and follow the protocol requirements;
  (null as Boolean /* UNSUPPORTED: human_judgment: consent / contraception / pregnancy workflow */)

define "Req Inc-2":  // inclusion; Age ≥18 years old;
  (AgeInYears() >= 18)

define "Req Inc-3":  // inclusion; Expected survival time ≥3 months;
  (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Inc-4":  // inclusion; Patients with unresectable or radical radiotherapy for locally advanced non-small cell lung cancer;
  (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Inc-5":  // inclusion; Documentation of EGFR sensitive mutations detected from tumor tissue or blood samples;
  ((null as Boolean /* UNSUPPORTED: biomarker: needs site genomic mapping / molecular matcher with assay & specimen adequacy */))

define "Req Inc-6":  // inclusion; Consent to provide archived tumor tissue samples or fresh tissue samples of primary or metastatic le
  ((null as Boolean /* UNSUPPORTED: biomarker: needs site genomic mapping / molecular matcher with assay & specimen adequacy */)
     and (null as Boolean /* UNSUPPORTED: text_dependent: residual text not covered by typed predicates */))

define "Req Inc-7":  // inclusion; At least one measurable lesion meeting the RECIST v1.1 definition was required;
  (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Inc-8":  // inclusion; ECOG 0 or 1;
  (if "ECOG latest" is null then null
    else FHIRHelpers.ToInteger("ECOG latest".value as FHIR.integer) in {0, 1})

define "Req Inc-9":  // inclusion; The toxicity of previous antineoplastic therapy has returned to ≤ grade 1 as defined by NCI-CTCAE v5
  (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Inc-10":  // inclusion; No severe cardiac dysfunction, left ventricular ejection fraction ≥50%;
  ((null as Boolean /* UNSUPPORTED: human_judgment: 'no severe cardiac dysfunction' (undefined) */)
     and (null as Boolean /* UNSUPPORTED: no LOINC binding for 'LVEF' (terminology unbound) */))

define "Req Inc-11":  // inclusion; The organ function level must meet the requirements on the premise that blood transfusion and colony
  (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Inc-12":  // inclusion; Urinary protein ≤2+ or < 1000mg/24h;
  ((null as Boolean /* UNSUPPORTED: no LOINC binding for 'Urinary protein (dipstick)' (terminology unbound) */)
     or (null as Boolean /* UNSUPPORTED: no LOINC binding for 'Urinary protein (24h)' (terminology unbound) */))

define "Req Inc-13":  // inclusion; For premenopausal women of childbearing potential, a pregnancy test must be performed within 7 days 
  (null as Boolean /* UNSUPPORTED: human_judgment: consent / contraception / pregnancy workflow */)

define "Req Exc-1":  // exclusion; Previous histologic or cytological evidence of small cell or mixed small/non-small cell components;
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-2":  // exclusion; Patients with previous systemic therapy;
  not (null as Boolean /* UNSUPPORTED: condition 'previous systemic therapy' has no terminology binding / evidence-adequacy policy */)

define "Req Exc-3":  // exclusion; Patients had received EGFR-TKI therapy;
  not (null as Boolean /* UNSUPPORTED: condition 'prior EGFR-TKI therapy' has no terminology binding / evidence-adequacy policy */)

define "Req Exc-4":  // exclusion; Studies received radical radiotherapy, major surgery, and large area radiotherapy within 4 weeks bef
  not (null as Boolean /* UNSUPPORTED: text_dependent: prior therapy / medication */)

define "Req Exc-5":  // exclusion; History of severe heart disease and cerebrovascular disease;
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-6":  // exclusion; Unstable thrombotic events requiring therapeutic intervention within 6 months before screening; Infu
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-7":  // exclusion; QT prolongation, complete left bundle branch block, III degree atrioventricular block, frequent and 
  not (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)

define "Req Exc-8":  // exclusion; Were diagnosed with active malignancy within 3 years before randomization;
  not (null as Boolean /* UNSUPPORTED: condition 'active malignancy' has no terminology binding / evidence-adequacy policy */)

define "Req Exc-9":  // exclusion; Hypertension poorly controlled by two antihypertensive drugs (systolic blood pressure > 150 mmHg or 
  not (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)

define "Req Exc-10":  // exclusion; Patients with poor glycemic control;
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-11":  // exclusion; A history of ILD requiring steroid therapy, or current ILD or grade ≥2 radiation pneumonitis, or a s
  not (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)

define "Req Exc-12":  // exclusion; Complicated with pulmonary diseases leading to clinically severe respiratory function impairment;
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-13":  // exclusion; Patients with active central nervous system metastasis;
  not (null as Boolean /* UNSUPPORTED: condition 'active CNS metastasis' has no terminology binding / evidence-adequacy policy */)

define "Req Exc-14":  // exclusion; Had a severe infection within 4 weeks before randomization;
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-15":  // exclusion; Patients with massive or symptomatic effusions or poorly controlled effusions;
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-16":  // exclusion; Imaging examination showed that the tumor had invaded or enveloped the large blood vessels in the ab
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-17":  // exclusion; Serious unhealed wound, ulcer, or fracture within 4 weeks before signing the informed consent;
  not (null as Boolean /* UNSUPPORTED: human_judgment: consent / contraception / pregnancy workflow */)

define "Req Exc-18":  // exclusion; Subjects with clinically significant bleeding or obvious bleeding tendency within 4 weeks before sig
  not (null as Boolean /* UNSUPPORTED: human_judgment: consent / contraception / pregnancy workflow */)

define "Req Exc-19":  // exclusion; Patients with a history of inflammatory bowel disease, extensive bowel resection, immune enteritis, 
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-20":  // exclusion; Patients with a history of allergy to recombinant humanized antibodies or to any of the excipients o
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-21":  // exclusion; Had autologous or allogeneic stem cell transplantation history;
  not (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)

define "Req Exc-22":  // exclusion; Human immunodeficiency virus antibody positive, active hepatitis B virus infection or hepatitis C vi
  not ((null as Boolean /* UNSUPPORTED: condition 'HIV antibody positive' has no terminology binding / evidence-adequacy policy */)
     or (null as Boolean /* UNSUPPORTED: condition 'active hepatitis B infection' has no terminology binding / evidence-adequacy policy */)
     or (null as Boolean /* UNSUPPORTED: condition 'active hepatitis C infection' has no terminology binding / evidence-adequacy policy */))

define "Req Exc-23":  // exclusion; A history of severe neurological or psychiatric illness;
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-24":  // exclusion; Received other unmarketed investigational drugs or treatments within 4 weeks before randomization;
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-25":  // exclusion; Subjects scheduled for vaccination or who received live vaccine within 28 days before study randomiz
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-26":  // exclusion; Other circumstances in which the investigator considered it inappropriate to participate in the tria
  not (null as Boolean /* UNSUPPORTED: human_judgment: investigator judgement */)

define "All Requirements Satisfied":  // ALL over requirement results; null = unresolved
  "Req Demo-min-age"
    and "Req Inc-1"
    and "Req Inc-2"
    and "Req Inc-3"
    and "Req Inc-4"
    and "Req Inc-5"
    and "Req Inc-6"
    and "Req Inc-7"
    and "Req Inc-8"
    and "Req Inc-9"
    and "Req Inc-10"
    and "Req Inc-11"
    and "Req Inc-12"
    and "Req Inc-13"
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
    and "Req Exc-15"
    and "Req Exc-16"
    and "Req Exc-17"
    and "Req Exc-18"
    and "Req Exc-19"
    and "Req Exc-20"
    and "Req Exc-21"
    and "Req Exc-22"
    and "Req Exc-23"
    and "Req Exc-24"
    and "Req Exc-25"
    and "Req Exc-26"

define "Requirement Outcomes":
  { Tuple { criterion: 'Demo-min-age', outcome: if "Req Demo-min-age" is null then 'unresolved' else if "Req Demo-min-age" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1', outcome: if "Req Inc-1" is null then 'unresolved' else if "Req Inc-1" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-2', outcome: if "Req Inc-2" is null then 'unresolved' else if "Req Inc-2" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-3', outcome: if "Req Inc-3" is null then 'unresolved' else if "Req Inc-3" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-4', outcome: if "Req Inc-4" is null then 'unresolved' else if "Req Inc-4" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-5', outcome: if "Req Inc-5" is null then 'unresolved' else if "Req Inc-5" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-6', outcome: if "Req Inc-6" is null then 'unresolved' else if "Req Inc-6" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-7', outcome: if "Req Inc-7" is null then 'unresolved' else if "Req Inc-7" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-8', outcome: if "Req Inc-8" is null then 'unresolved' else if "Req Inc-8" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-9', outcome: if "Req Inc-9" is null then 'unresolved' else if "Req Inc-9" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-10', outcome: if "Req Inc-10" is null then 'unresolved' else if "Req Inc-10" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-11', outcome: if "Req Inc-11" is null then 'unresolved' else if "Req Inc-11" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-12', outcome: if "Req Inc-12" is null then 'unresolved' else if "Req Inc-12" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-13', outcome: if "Req Inc-13" is null then 'unresolved' else if "Req Inc-13" then 'satisfied' else 'violated' },
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
  Tuple { criterion: 'Exc-14', outcome: if "Req Exc-14" is null then 'unresolved' else if "Req Exc-14" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-15', outcome: if "Req Exc-15" is null then 'unresolved' else if "Req Exc-15" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-16', outcome: if "Req Exc-16" is null then 'unresolved' else if "Req Exc-16" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-17', outcome: if "Req Exc-17" is null then 'unresolved' else if "Req Exc-17" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-18', outcome: if "Req Exc-18" is null then 'unresolved' else if "Req Exc-18" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-19', outcome: if "Req Exc-19" is null then 'unresolved' else if "Req Exc-19" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-20', outcome: if "Req Exc-20" is null then 'unresolved' else if "Req Exc-20" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-21', outcome: if "Req Exc-21" is null then 'unresolved' else if "Req Exc-21" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-22', outcome: if "Req Exc-22" is null then 'unresolved' else if "Req Exc-22" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-23', outcome: if "Req Exc-23" is null then 'unresolved' else if "Req Exc-23" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-24', outcome: if "Req Exc-24" is null then 'unresolved' else if "Req Exc-24" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-25', outcome: if "Req Exc-25" is null then 'unresolved' else if "Req Exc-25" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Exc-26', outcome: if "Req Exc-26" is null then 'unresolved' else if "Req Exc-26" then 'satisfied' else 'violated' } }

define "Any Requirement Violated":
  exists ("Requirement Outcomes" O where O.outcome = 'violated')
