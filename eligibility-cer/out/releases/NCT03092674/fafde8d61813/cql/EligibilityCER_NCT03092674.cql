// Gated: only dual-approved (validated) criteria are compiled; the rest return null (unresolved).
// Source: ClinicalTrials.gov NCT03092674 (baseline: registry_excerpt); CER sha256 4061ef132f64; lifecycle draft
library EligibilityCER_NCT03092674 version '0.1.0-gated'
using FHIR version '4.0.1'
include FHIRHelpers version '4.0.1' called FHIRHelpers
codesystem "LOINC": 'http://loinc.org'
codesystem "SNOMED CT": 'http://snomed.info/sct'
context Patient


define "Req Demo-min-age":  // inclusion; minimumAge: 60 Years
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b1":  // inclusion; REGISTRATION STEP 1-SPECIMEN SUBMISSION
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b2":  // inclusion; Patients must be suspected to have previously untreated acute myelogenous leukemia (AML) or myelodys
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b3":  // inclusion; Patients must not be known to have AML in the central nervous system (CNS)
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b4":  // inclusion; Patients must have specimens submitted for FLT3 testing for randomization stratification; collection
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b5":  // inclusion; Patients must be offered participation in specimen banking; with patient consent, pretreatment speci
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b6":  // inclusion; Patients who have received prior therapy with midostaurin, any anti-PD-1 or anti-PD-L1 therapy, any 
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b7":  // inclusion; Patients must be able to swallow oral medications without crushing or chewing
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b8":  // inclusion; Prior malignancy is allowed providing it does not require concurrent therapy
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b9":  // inclusion; Patients must not be pregnant or nursing; women/men of reproductive potential must have agreed to us
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b10":  // inclusion; Patients must be informed of the investigational nature of this study and must sign and give written
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b11":  // inclusion; As a part of the Oncology Patient Enrollment Network (OPEN) registration process the treating instit
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b12":  // inclusion; REGISTRATION STEP 2-RANDOMIZATION: Patients must be registered to Step 2 no more than 42 days after 
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b13":  // inclusion; REGISTRATION STEP 2-RANDOMIZATION: Patients must have morphologically confirmed, previously untreate
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b14":  // inclusion; REGISTRATION STEP 2-RANDOMIZATION: Patients must not be known to have AML in the CNS
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b15":  // inclusion; REGISTRATION STEP 2-RANDOMIZATION: Patients must be deemed, in the judgment of the treating physicia
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b16":  // inclusion; REGISTRATION STEP 2-RANDOMIZATION: Pretreatment cytogenetics must be performed on all patients; coll
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b17":  // inclusion; REGISTRATION STEP 2-RANDOMIZATION: FLT3 results will be used for stratification purposes at the time
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b18":  // inclusion; REGISTRATION STEP 2-RANDOMIZATION: Prior treatment with hydroxyurea is permitted; prior all-trans re
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b19":  // inclusion; REGISTRATION STEP 2-RANDOMIZATION: Patients may have received non-intensive therapy for antecedent h
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b20":  // inclusion; REGISTRATION STEP 2-RANDOMIZATION: Patients who are transfusion-dependent and patients receiving gro
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b21":  // inclusion; REGISTRATION STEP 2-RANDOMIZATION: The following tests must be performed within 14 days prior to ran
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b22":  // inclusion; REGISTRATION STEP 2-RANDOMIZATION: Patients must have complete history and physical examination with
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b23":  // inclusion; REGISTRATION STEP 2-RANDOMIZATION: Patients must not have active infection (systemic bacterial, fung
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b24":  // inclusion; REGISTRATION STEP 2-RANDOMIZATION: Patients must be eligible for at least one of the currently activ
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b25":  // inclusion; REGISTRATION STEP 2-RANDOMIZATION: Patients must be informed of the investigational nature of this s
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b26":  // inclusion; ARM B (AZACITIDINE + NIVOLUMAB)
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b27":  // inclusion; Patients must not have active autoimmune disease that has required systemic treatment in past 2 year
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b28":  // inclusion; Patients must have AST and ALT =< 2.5 x institutional upper limit of normal (IULN)
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b29":  // inclusion; Patients must have total bilirubin =< 1.5 x IULN
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b30":  // inclusion; Patients must have baseline troponin test performed for eligibility; however, no associated values m
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b31":  // inclusion; ARM C (AZACITIDINE + MIDOSTAURIN)
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b32":  // inclusion; Patients must have total bilirubin =< 2.5 x IULN
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b33":  // inclusion; Patients must have creatinine clearance =< 2.5 x IULN
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b34":  // inclusion; Patients must have corrected QT (QTc) interval < 500/msec (by Bazett's formula) on baseline ECG
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b35":  // inclusion; Patients must not have any history of hypersensitivity to any drugs or metabolites of midostaurin
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b36":  // inclusion; All tests for establishing baseline values must be completed within 14 days prior to registration to
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

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
    and "Req Inc-b9"
    and "Req Inc-b10"
    and "Req Inc-b11"
    and "Req Inc-b12"
    and "Req Inc-b13"
    and "Req Inc-b14"
    and "Req Inc-b15"
    and "Req Inc-b16"
    and "Req Inc-b17"
    and "Req Inc-b18"
    and "Req Inc-b19"
    and "Req Inc-b20"
    and "Req Inc-b21"
    and "Req Inc-b22"
    and "Req Inc-b23"
    and "Req Inc-b24"
    and "Req Inc-b25"
    and "Req Inc-b26"
    and "Req Inc-b27"
    and "Req Inc-b28"
    and "Req Inc-b29"
    and "Req Inc-b30"
    and "Req Inc-b31"
    and "Req Inc-b32"
    and "Req Inc-b33"
    and "Req Inc-b34"
    and "Req Inc-b35"
    and "Req Inc-b36"

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
  Tuple { criterion: 'Inc-b9', outcome: if "Req Inc-b9" is null then 'unresolved' else if "Req Inc-b9" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b10', outcome: if "Req Inc-b10" is null then 'unresolved' else if "Req Inc-b10" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b11', outcome: if "Req Inc-b11" is null then 'unresolved' else if "Req Inc-b11" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b12', outcome: if "Req Inc-b12" is null then 'unresolved' else if "Req Inc-b12" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b13', outcome: if "Req Inc-b13" is null then 'unresolved' else if "Req Inc-b13" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b14', outcome: if "Req Inc-b14" is null then 'unresolved' else if "Req Inc-b14" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b15', outcome: if "Req Inc-b15" is null then 'unresolved' else if "Req Inc-b15" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b16', outcome: if "Req Inc-b16" is null then 'unresolved' else if "Req Inc-b16" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b17', outcome: if "Req Inc-b17" is null then 'unresolved' else if "Req Inc-b17" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b18', outcome: if "Req Inc-b18" is null then 'unresolved' else if "Req Inc-b18" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b19', outcome: if "Req Inc-b19" is null then 'unresolved' else if "Req Inc-b19" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b20', outcome: if "Req Inc-b20" is null then 'unresolved' else if "Req Inc-b20" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b21', outcome: if "Req Inc-b21" is null then 'unresolved' else if "Req Inc-b21" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b22', outcome: if "Req Inc-b22" is null then 'unresolved' else if "Req Inc-b22" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b23', outcome: if "Req Inc-b23" is null then 'unresolved' else if "Req Inc-b23" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b24', outcome: if "Req Inc-b24" is null then 'unresolved' else if "Req Inc-b24" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b25', outcome: if "Req Inc-b25" is null then 'unresolved' else if "Req Inc-b25" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b26', outcome: if "Req Inc-b26" is null then 'unresolved' else if "Req Inc-b26" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b27', outcome: if "Req Inc-b27" is null then 'unresolved' else if "Req Inc-b27" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b28', outcome: if "Req Inc-b28" is null then 'unresolved' else if "Req Inc-b28" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b29', outcome: if "Req Inc-b29" is null then 'unresolved' else if "Req Inc-b29" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b30', outcome: if "Req Inc-b30" is null then 'unresolved' else if "Req Inc-b30" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b31', outcome: if "Req Inc-b31" is null then 'unresolved' else if "Req Inc-b31" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b32', outcome: if "Req Inc-b32" is null then 'unresolved' else if "Req Inc-b32" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b33', outcome: if "Req Inc-b33" is null then 'unresolved' else if "Req Inc-b33" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b34', outcome: if "Req Inc-b34" is null then 'unresolved' else if "Req Inc-b34" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b35', outcome: if "Req Inc-b35" is null then 'unresolved' else if "Req Inc-b35" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-b36', outcome: if "Req Inc-b36" is null then 'unresolved' else if "Req Inc-b36" then 'satisfied' else 'violated' } }

define "Any Requirement Violated":
  exists ("Requirement Outcomes" O where O.outcome = 'violated')
