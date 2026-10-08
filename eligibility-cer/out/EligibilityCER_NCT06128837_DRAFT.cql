// DRAFT: includes criteria that are NOT validated. Not for screening use.
// Source: ClinicalTrials.gov NCT06128837 (baseline: registry_excerpt); CER sha256 4a73219730ff; lifecycle draft
library EligibilityCER_NCT06128837_DRAFT version '0.1.0-draft'
using FHIR version '4.0.1'
include FHIRHelpers version '4.0.1' called FHIRHelpers
codesystem "LOINC": 'http://loinc.org'
codesystem "SNOMED CT": 'http://snomed.info/sct'
code "ECOG (89247-1)": '89247-1' from "LOINC" display 'ECOG Performance Status score'
code "ANC (751-8)": '751-8' from "LOINC" display 'ANC'
code "Platelets (777-3)": '777-3' from "LOINC" display 'Platelets'
code "Hemoglobin (718-7)": '718-7' from "LOINC" display 'Hemoglobin'
code "Total bilirubin (1975-2)": '1975-2' from "LOINC" display 'Total bilirubin'
code "AST (1920-8)": '1920-8' from "LOINC" display 'AST'
code "ALT (1742-6)": '1742-6' from "LOINC" display 'ALT'
code "Albumin (1751-7)": '1751-7' from "LOINC" display 'Albumin'
code "Creatinine (2160-0)": '2160-0' from "LOINC" display 'Creatinine'
code "Creatinine clearance (2164-2)": '2164-2' from "LOINC" display 'Creatinine clearance'
code "INR (6301-6)": '6301-6' from "LOINC" display 'INR'
parameter "ScreeningDate" DateTime  // no default on purpose: a missing anchor is unknown, not today
parameter "LabMaxAgeDays" Integer default 90  // site evidence-freshness policy
context Patient


define "ECOG latest":
  Last([Observation: "ECOG (89247-1)"] O
    where O.status.value in {'final', 'amended', 'corrected'}
      and days between FHIRHelpers.ToDateTime(O.effective as FHIR.dateTime) and "ScreeningDate" in Interval[0, "LabMaxAgeDays"]
    sort by FHIRHelpers.ToDateTime(effective as FHIR.dateTime))

define "ANC latest":
  Last([Observation: "ANC (751-8)"] O
    where O.status.value in {'final', 'amended', 'corrected'}
      and days between FHIRHelpers.ToDateTime(O.effective as FHIR.dateTime) and "ScreeningDate" in Interval[0, "LabMaxAgeDays"]
    sort by FHIRHelpers.ToDateTime(effective as FHIR.dateTime))

define "Platelets latest":
  Last([Observation: "Platelets (777-3)"] O
    where O.status.value in {'final', 'amended', 'corrected'}
      and days between FHIRHelpers.ToDateTime(O.effective as FHIR.dateTime) and "ScreeningDate" in Interval[0, "LabMaxAgeDays"]
    sort by FHIRHelpers.ToDateTime(effective as FHIR.dateTime))

define "Hemoglobin latest":
  Last([Observation: "Hemoglobin (718-7)"] O
    where O.status.value in {'final', 'amended', 'corrected'}
      and days between FHIRHelpers.ToDateTime(O.effective as FHIR.dateTime) and "ScreeningDate" in Interval[0, "LabMaxAgeDays"]
    sort by FHIRHelpers.ToDateTime(effective as FHIR.dateTime))

define "Total bilirubin latest":
  Last([Observation: "Total bilirubin (1975-2)"] O
    where O.status.value in {'final', 'amended', 'corrected'}
      and days between FHIRHelpers.ToDateTime(O.effective as FHIR.dateTime) and "ScreeningDate" in Interval[0, "LabMaxAgeDays"]
    sort by FHIRHelpers.ToDateTime(effective as FHIR.dateTime))

define "AST latest":
  Last([Observation: "AST (1920-8)"] O
    where O.status.value in {'final', 'amended', 'corrected'}
      and days between FHIRHelpers.ToDateTime(O.effective as FHIR.dateTime) and "ScreeningDate" in Interval[0, "LabMaxAgeDays"]
    sort by FHIRHelpers.ToDateTime(effective as FHIR.dateTime))

define "ALT latest":
  Last([Observation: "ALT (1742-6)"] O
    where O.status.value in {'final', 'amended', 'corrected'}
      and days between FHIRHelpers.ToDateTime(O.effective as FHIR.dateTime) and "ScreeningDate" in Interval[0, "LabMaxAgeDays"]
    sort by FHIRHelpers.ToDateTime(effective as FHIR.dateTime))

define "Albumin latest":
  Last([Observation: "Albumin (1751-7)"] O
    where O.status.value in {'final', 'amended', 'corrected'}
      and days between FHIRHelpers.ToDateTime(O.effective as FHIR.dateTime) and "ScreeningDate" in Interval[0, "LabMaxAgeDays"]
    sort by FHIRHelpers.ToDateTime(effective as FHIR.dateTime))

define "Creatinine latest":
  Last([Observation: "Creatinine (2160-0)"] O
    where O.status.value in {'final', 'amended', 'corrected'}
      and days between FHIRHelpers.ToDateTime(O.effective as FHIR.dateTime) and "ScreeningDate" in Interval[0, "LabMaxAgeDays"]
    sort by FHIRHelpers.ToDateTime(effective as FHIR.dateTime))

define "Creatinine clearance latest":
  Last([Observation: "Creatinine clearance (2164-2)"] O
    where O.status.value in {'final', 'amended', 'corrected'}
      and days between FHIRHelpers.ToDateTime(O.effective as FHIR.dateTime) and "ScreeningDate" in Interval[0, "LabMaxAgeDays"]
    sort by FHIRHelpers.ToDateTime(effective as FHIR.dateTime))

define "INR latest":
  Last([Observation: "INR (6301-6)"] O
    where O.status.value in {'final', 'amended', 'corrected'}
      and days between FHIRHelpers.ToDateTime(O.effective as FHIR.dateTime) and "ScreeningDate" in Interval[0, "LabMaxAgeDays"]
    sort by FHIRHelpers.ToDateTime(effective as FHIR.dateTime))

define "Req Demo-min-age":  // inclusion; minimumAge: 18 Years
  (AgeInYears() >= 18)

define "Req Inc-1":  // inclusion; Age ≥ 18 years, male or female;
  (AgeInYears() >= 18)

define "Req Inc-2":  // inclusion; Patients with histologically and/or cytologically confirmed small cell lung cancer;
  (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Inc-3":  // inclusion; Disease progression (CTFI ≥ 30 days and ≤ 6 months) occurred after at least 4 cycles of first-line e
  (null as Boolean /* UNSUPPORTED: human_judgment: investigator judgement */)

define "Req Inc-4":  // inclusion; At least one evaluable lesion (according to RECIST 1.1 criteria);
  (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Inc-5":  // inclusion; Expected survival time ≥ 3 months;
  (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Inc-6":  // inclusion; Eastern Cooperative Oncology Group (ECOG) score < 2;
  (if "ECOG latest" is null then null
    else FHIRHelpers.ToInteger("ECOG latest".value as FHIR.integer) in {0, 1})

define "Req Inc-7":  // inclusion; Patients who received no liver metastasis; or the number of liver metastases was ≤ 3 and the longest
  (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Inc-8":  // inclusion; Patients with brain metastasis at baseline should meet all the following conditions: lesions not inv
  (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)

define "Req Inc-9":  // inclusion; Organ function meeting the following criteria at screening: a.Blood routine: neutrophil (ANC) ≥ 1.5 
  (((if "ANC latest" is null then null
    else FHIRHelpers.ToQuantity("ANC latest".value as FHIR.Quantity) >= 1.5 '10*9/L')
     and (if "Platelets latest" is null then null
    else FHIRHelpers.ToQuantity("Platelets latest".value as FHIR.Quantity) >= 100 '10*9/L')
     and (if "Hemoglobin latest" is null then null
    else FHIRHelpers.ToQuantity("Hemoglobin latest".value as FHIR.Quantity) >= 90 'g/L'))
     and ((if "Total bilirubin latest" is null or "Total bilirubin latest".referenceRange[0].high.value is null then null
    else FHIRHelpers.ToDecimal(("Total bilirubin latest".value as FHIR.Quantity).value) <= 1 * FHIRHelpers.ToDecimal("Total bilirubin latest".referenceRange[0].high.value))
     and (if "AST latest" is null or "AST latest".referenceRange[0].high.value is null then null
    else FHIRHelpers.ToDecimal(("AST latest".value as FHIR.Quantity).value) <= 2 * FHIRHelpers.ToDecimal("AST latest".referenceRange[0].high.value))
     and (if "ALT latest" is null or "ALT latest".referenceRange[0].high.value is null then null
    else FHIRHelpers.ToDecimal(("ALT latest".value as FHIR.Quantity).value) <= 2 * FHIRHelpers.ToDecimal("ALT latest".referenceRange[0].high.value))
     and (null as Boolean /* UNSUPPORTED: conditional applicability needs an explicit applicability fact */)
     and (null as Boolean /* UNSUPPORTED: conditional applicability needs an explicit applicability fact */)
     and (if "Albumin latest" is null then null
    else FHIRHelpers.ToQuantity("Albumin latest".value as FHIR.Quantity) >= 30 'g/L'))
     and ((if "Creatinine latest" is null or "Creatinine latest".referenceRange[0].high.value is null then null
    else FHIRHelpers.ToDecimal(("Creatinine latest".value as FHIR.Quantity).value) <= 1.5 * FHIRHelpers.ToDecimal("Creatinine latest".referenceRange[0].high.value))
     or (if "Creatinine clearance latest" is null then null
    else FHIRHelpers.ToQuantity("Creatinine clearance latest".value as FHIR.Quantity) >= 40 'mL/min'))
     and (null as Boolean /* UNSUPPORTED: unit missing or not UCUM-like */))

define "Req Inc-10":  // inclusion; Has fully understood and voluntarily signed a written informed consent form for this study and is ab
  (null as Boolean /* UNSUPPORTED: human_judgment: consent / contraception / pregnancy workflow */)

define "Req Inc-11":  // inclusion; Female subjects of childbearing potential and male subjects with partners of childbearing potential 
  (null as Boolean /* UNSUPPORTED: human_judgment: consent / contraception / pregnancy workflow */)

define "Req Exc-1":  // exclusion; Pathological diagnosis of compound small cell lung cancer;
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-2":  // exclusion; Patients with meningeal metastasis, spinal cord tumor invasion, spinal cord compression syndrome;
  not (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)

define "Req Exc-3":  // exclusion; Superior vena cava syndrome with symptoms or significantly aggravated imaging, which may require rad
  not (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)

define "Req Exc-4":  // exclusion; Active infection (including tuberculosis infection) requiring systemic anti-bacterial, antifungal, a
  not (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)

define "Req Exc-5":  // exclusion; Recurrent symptomatic poorly controlled chronic obstructive pulmonary disease, extensive interstitia
  not (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)

define "Req Exc-6":  // exclusion; Extensive radiation pneumonitis, pulmonary embolism or active massive hemoptysis; Patients with seve
  not (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)

define "Req Exc-7":  // exclusion; Patients with the following cardiovascular and cerebrovascular diseases or history:
  not ((null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)
     or (null as Boolean /* UNSUPPORTED: condition 'arrhythmia' has no terminology binding */)
     or (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */))

define "Req Exc-8":  // exclusion; Patients with any of the following conditions:
  not ((null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)
     or (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)
     or (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */))

define "Req Exc-9":  // exclusion; Other malignancies within 5 years before screening (except cured stage IB or lower cervical cancer, 
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-10":  // exclusion; Patients with primary diseases of other important organs (such as nervous system, cardiovascular and
  not (null as Boolean /* UNSUPPORTED: human_judgment: investigator judgement */)

define "Req Exc-11":  // exclusion; Previous treatment with irinotecan or irinotecan modified, topotecan or other topoisomerase I inhibi
  not (null as Boolean /* UNSUPPORTED: text_dependent: prior therapy / medication */)

define "Req Exc-12":  // exclusion; Known hypersensitivity to irinotecan hydrochloride liposomes or its excipients, structurally similar
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-13":  // exclusion; Those who have been vaccinated with live vaccine or live attenuated vaccine before screening;
  not (null as Boolean /* UNSUPPORTED: text_dependent: prior therapy / medication */)

define "Req Exc-14":  // exclusion; Patients who have received systemic anti-tumor therapy in 4 weeks before randomization;
  not (null as Boolean /* UNSUPPORTED: text_dependent: prior therapy / medication */)

define "Req Exc-15":  // exclusion; Patients who have applied other clinical trial drugs/devices before randomization;
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-16":  // exclusion; Patients who have used strong inducers or strong inhibitors of CYP3A4 and strong inhibitors of UGT1A
  not (null as Boolean /* UNSUPPORTED: text_dependent: prior therapy / medication */)

define "Req Exc-17":  // exclusion; Adverse reactions caused by previous anti-tumor treatment are not recovered to grade 1 or lower (exc
  not (null as Boolean /* UNSUPPORTED: text_dependent: unclassified narrative */)

define "Req Exc-18":  // exclusion; History of drug abuse, drug abuse and/or alcoholism;
  not (null as Boolean /* UNSUPPORTED: text_dependent: clinical condition (terminology unbound) */)

define "Req Exc-19":  // exclusion; Pregnant or lactating women;
  not (null as Boolean /* UNSUPPORTED: human_judgment: consent / contraception / pregnancy workflow */)

define "Req Exc-20":  // exclusion; Other conditions (including but not limited to unstable nervous system diseases and mental disorders
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
  Tuple { criterion: 'Exc-20', outcome: if "Req Exc-20" is null then 'unresolved' else if "Req Exc-20" then 'satisfied' else 'violated' } }

define "Any Requirement Violated":
  exists ("Requirement Outcomes" O where O.outcome = 'violated')
