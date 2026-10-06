// Gated: only dual-approved (validated) criteria are compiled; the rest return null (unresolved).
// Source: ClinicalTrials.gov NCT03055013 (baseline: registry_excerpt); CER sha256 c8901f786988; lifecycle draft
library EligibilityCER_NCT03055013 version '0.1.0-gated'
using FHIR version '4.0.1'
include FHIRHelpers version '4.0.1' called FHIRHelpers
codesystem "LOINC": 'http://loinc.org'
codesystem "SNOMED CT": 'http://snomed.info/sct'
context Patient


define "Req Demo-min-age":  // inclusion; minimumAge: 18 Years
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b1":  // inclusion; ELIGIBILITY CRITERIA FOR RANDOMIZATION:
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b2":  // inclusion; Patients must have a renal mass consistent with a clinical stage >= T2Nx renal cell carcinoma (RCC) 
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b3":  // inclusion; Patients must have no clinical or radiological evidence of distant metastases (M0) unless the presum
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b4":  // inclusion; If histological confirmation of RCC has not been done within 12 months prior to randomization, patie
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b5":  // inclusion; Patient must not have any prior systemic or local anti-cancer therapy for the current RCC
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b6":  // inclusion; Patient must be >= 18 years of age. Because no dosing or adverse event data are currently available 
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b7":  // inclusion; Patient must have an Eastern Cooperative Oncology Group (ECOG) performance status of 0 or 1
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b8":  // inclusion; Patient must not have a prior history of RCC that was treated with curative intent within the past 5
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b9":  // inclusion; Patients cannot have concurrent malignancies, with the following exceptions:
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b10":  // inclusion; Patient must not have active known or suspected autoimmune disease. The following autoimmune disorde
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b11":  // inclusion; Patient must not have any ongoing condition requiring systemic treatment with either corticosteroids
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b12":  // inclusion; Patient must not have uncontrolled adrenal insufficiency
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b13":  // inclusion; Patient must not have known evidence of chronic active liver disease or evidence of acute or chronic
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b14":  // inclusion; Patient must not have any serious intercurrent illness, including ongoing or active infection requir
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b15":  // inclusion; Patient must not have known evidence of human immunodeficiency virus (HIV) infection, since the effe
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b16":  // inclusion; Patient must not have any known medical condition (e.g. a condition associated with uncontrolled dia
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b17":  // inclusion; Patient must not have had any major surgery within 28 days prior to randomization
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b18":  // inclusion; Patient must not be currently enrolled in other clinical trials testing a therapeutic intervention
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b19":  // inclusion; Patient must not have any history of severe hypersensitivity to a monoclonal antibody
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b20":  // inclusion; Patient must have the ability to understand and the willingness to sign a written informed consent d
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b21":  // inclusion; Patients must not be pregnant or breast-feeding, as the effects of nivolumab on the developing human
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b22":  // inclusion; Patients must not expect to conceive or father children by using accepted and effective method(s) of
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b23":  // inclusion; White blood cells >= 2000/uL (within 8 weeks prior to randomization)
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b24":  // inclusion; Absolute neutrophil count (ANC) >= 1,500/mm\^3 (within 8 weeks prior to randomization)
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b25":  // inclusion; Platelet count >= 100,000/mm\^3 (within 8 weeks prior to randomization)
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b26":  // inclusion; Hemoglobin >= 9.0 g/dL (within 8 weeks prior to randomization)
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b27":  // inclusion; Serum creatinine =< 1.5 x upper limit of normal (ULN) or calculated creatinine clearance (CrCl) >= 4
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b28":  // inclusion; Total bilirubin =< 1.5 x ULN (except subjects with Gilbert syndrome, who can have total bilirubin < 
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-b29":  // inclusion; Aspartate aminotransferase (AST) and alanine aminotransferase (ALT) =< 2.5 x ULN (within 8 weeks pri
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
  Tuple { criterion: 'Inc-b29', outcome: if "Req Inc-b29" is null then 'unresolved' else if "Req Inc-b29" then 'satisfied' else 'violated' } }

define "Any Requirement Violated":
  exists ("Requirement Outcomes" O where O.outcome = 'violated')
