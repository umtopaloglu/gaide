// Gated: only dual-approved (validated) criteria are compiled; the rest return null (unresolved).
// Source: ClinicalTrials.gov NCT05512364 (baseline: registry_excerpt); CER sha256 7f692e2377cc; lifecycle draft
library EligibilityCER_NCT05512364_ctdna_screening_phase version '0.1.0-gated'
using FHIR version '4.0.1'
include FHIRHelpers version '4.0.1' called FHIRHelpers
codesystem "LOINC": 'http://loinc.org'
codesystem "SNOMED CT": 'http://snomed.info/sct'
context Patient


define "Req Demo-min-age":  // inclusion; minimumAge: 18 Years
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b1":  // inclusion; Female (both pre- and postmenopausal) or male patients with histologically confirmed ER positive (re
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b2":  // inclusion; ER-positive defined as ≥ 10% of cells staining positive for ER or Allred proportion score ≥3
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b3":  // inclusion; HER2-negative defined as a score of 0, 1+ by immunohistochemistry (IHC) or a negative in situ hybrid
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b4":  // inclusion; Intermediate to high risk of recurrence after definitive treatment for early breast cancer, defined 
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b5":  // inclusion; Any patient with ≥ 4 positive axillary lymph nodes (stage pN2-3).
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b6":  // inclusion; 1-3 positive axillary lymph nodes (stage pN1) and either:
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b7":  // inclusion; Tumour size ≥ 5 cm or/and
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b8":  // inclusion; Histologic grade 3 or/and
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b9":  // inclusion; Ki67≥20% or/and
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b10":  // inclusion; High genomic risk defined as Oncotype Dx Recurrence Score >=26, Mammaprint high risk, Prosigna score
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b11":  // inclusion; Negative axillary lymph nodes (stage pN0) and tumour size ≥ 2 cm and either
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b12":  // inclusion; Histologic grade 3 a or/and
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b13":  // inclusion; Ki67≥20% and/or
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b14":  // inclusion; High genomic risk defined as Oncotype Dx Recurrence Score >=26, Mammaprint high risk, Prosigna score
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b15":  // inclusion; Patient may have received neoadjuvant endocrine therapy or neoadjuvant chemotherapy provided that:
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b16":  // inclusion; The initial tumour and/or the tumour after surgery meet the criteria above defined for patients trea
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b17":  // inclusion; There is no pathological complete response, defined as no invasive disease in the breast and axilla 
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b18":  // inclusion; Age ≥18 years
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b19":  // inclusion; Patients must have received at least 1 year and up to 7.5 years of ET and planned to continue adjuva
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b20":  // inclusion; Previous adjuvant CDK4/6 inhibitor or PARP-inhibitor treatment is allowed provided it is completed
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b21":  // inclusion; Invasive multicentric / multifocal disease is allowed provided that all the tested foci are ER+ HER2
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b22":  // inclusion; Available tumour sample from resected or biopsied tissue, with a tumour content of ≥20% (30% preferr
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b23":  // inclusion; Core Needle Biopsies (CNB): recommended minimum of four (4) cores per block
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b24":  // inclusion; Fine Needle Aspirates (FNA) are not accepted
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b25":  // inclusion; The following sample types are acceptable:
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b26":  // inclusion; 6-10 unstained slides (charged and unbaked) of 10μm each (or 12-19 unstained slides at 5 μm each), P
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b27":  // inclusion; FFPE tissue block with 25mm2 minimum surface area
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b1.b28":  // inclusion; Written informed consent must be given according to ICH/GCP, and national/local regulations.
  (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b2.b1":  // exclusion; Suspected recurrent disease or known conflicts with the inclusion and exclusion criteria for the ran
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b2.b2":  // exclusion; Prior treatment with any SERD or investigational ER antagonist
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b2.b3":  // exclusion; Previous history of invasive breast cancer
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b2.b4":  // exclusion; Previous history of any other malignancy within the last 5 years, except for adequately treated basa
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b2.b5":  // exclusion; Previous history of bone marrow and/or organ transplant
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b2.b6":  // exclusion; Bilateral invasive breast cancer
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b2.b7":  // exclusion; Participation in another clinical study, with the exception of the SURVIVE study and observational (
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "Req Inc-1.b2.b8":  // exclusion; Blood transfusion within 3 months prior to registration or during the screening.
  not (null as Boolean /* NOT VALIDATED: dual clinical+informatics approval required before compilation */)

define "All Requirements Satisfied":  // ALL over requirement results; null = unresolved
  "Req Demo-min-age"
    and "Req Inc-1.b1.b1"
    and "Req Inc-1.b1.b2"
    and "Req Inc-1.b1.b3"
    and "Req Inc-1.b1.b4"
    and "Req Inc-1.b1.b5"
    and "Req Inc-1.b1.b6"
    and "Req Inc-1.b1.b7"
    and "Req Inc-1.b1.b8"
    and "Req Inc-1.b1.b9"
    and "Req Inc-1.b1.b10"
    and "Req Inc-1.b1.b11"
    and "Req Inc-1.b1.b12"
    and "Req Inc-1.b1.b13"
    and "Req Inc-1.b1.b14"
    and "Req Inc-1.b1.b15"
    and "Req Inc-1.b1.b16"
    and "Req Inc-1.b1.b17"
    and "Req Inc-1.b1.b18"
    and "Req Inc-1.b1.b19"
    and "Req Inc-1.b1.b20"
    and "Req Inc-1.b1.b21"
    and "Req Inc-1.b1.b22"
    and "Req Inc-1.b1.b23"
    and "Req Inc-1.b1.b24"
    and "Req Inc-1.b1.b25"
    and "Req Inc-1.b1.b26"
    and "Req Inc-1.b1.b27"
    and "Req Inc-1.b1.b28"
    and "Req Inc-1.b2.b1"
    and "Req Inc-1.b2.b2"
    and "Req Inc-1.b2.b3"
    and "Req Inc-1.b2.b4"
    and "Req Inc-1.b2.b5"
    and "Req Inc-1.b2.b6"
    and "Req Inc-1.b2.b7"
    and "Req Inc-1.b2.b8"

define "Requirement Outcomes":
  { Tuple { criterion: 'Demo-min-age', outcome: if "Req Demo-min-age" is null then 'unresolved' else if "Req Demo-min-age" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b1', outcome: if "Req Inc-1.b1.b1" is null then 'unresolved' else if "Req Inc-1.b1.b1" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b2', outcome: if "Req Inc-1.b1.b2" is null then 'unresolved' else if "Req Inc-1.b1.b2" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b3', outcome: if "Req Inc-1.b1.b3" is null then 'unresolved' else if "Req Inc-1.b1.b3" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b4', outcome: if "Req Inc-1.b1.b4" is null then 'unresolved' else if "Req Inc-1.b1.b4" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b5', outcome: if "Req Inc-1.b1.b5" is null then 'unresolved' else if "Req Inc-1.b1.b5" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b6', outcome: if "Req Inc-1.b1.b6" is null then 'unresolved' else if "Req Inc-1.b1.b6" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b7', outcome: if "Req Inc-1.b1.b7" is null then 'unresolved' else if "Req Inc-1.b1.b7" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b8', outcome: if "Req Inc-1.b1.b8" is null then 'unresolved' else if "Req Inc-1.b1.b8" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b9', outcome: if "Req Inc-1.b1.b9" is null then 'unresolved' else if "Req Inc-1.b1.b9" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b10', outcome: if "Req Inc-1.b1.b10" is null then 'unresolved' else if "Req Inc-1.b1.b10" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b11', outcome: if "Req Inc-1.b1.b11" is null then 'unresolved' else if "Req Inc-1.b1.b11" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b12', outcome: if "Req Inc-1.b1.b12" is null then 'unresolved' else if "Req Inc-1.b1.b12" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b13', outcome: if "Req Inc-1.b1.b13" is null then 'unresolved' else if "Req Inc-1.b1.b13" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b14', outcome: if "Req Inc-1.b1.b14" is null then 'unresolved' else if "Req Inc-1.b1.b14" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b15', outcome: if "Req Inc-1.b1.b15" is null then 'unresolved' else if "Req Inc-1.b1.b15" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b16', outcome: if "Req Inc-1.b1.b16" is null then 'unresolved' else if "Req Inc-1.b1.b16" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b17', outcome: if "Req Inc-1.b1.b17" is null then 'unresolved' else if "Req Inc-1.b1.b17" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b18', outcome: if "Req Inc-1.b1.b18" is null then 'unresolved' else if "Req Inc-1.b1.b18" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b19', outcome: if "Req Inc-1.b1.b19" is null then 'unresolved' else if "Req Inc-1.b1.b19" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b20', outcome: if "Req Inc-1.b1.b20" is null then 'unresolved' else if "Req Inc-1.b1.b20" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b21', outcome: if "Req Inc-1.b1.b21" is null then 'unresolved' else if "Req Inc-1.b1.b21" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b22', outcome: if "Req Inc-1.b1.b22" is null then 'unresolved' else if "Req Inc-1.b1.b22" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b23', outcome: if "Req Inc-1.b1.b23" is null then 'unresolved' else if "Req Inc-1.b1.b23" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b24', outcome: if "Req Inc-1.b1.b24" is null then 'unresolved' else if "Req Inc-1.b1.b24" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b25', outcome: if "Req Inc-1.b1.b25" is null then 'unresolved' else if "Req Inc-1.b1.b25" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b26', outcome: if "Req Inc-1.b1.b26" is null then 'unresolved' else if "Req Inc-1.b1.b26" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b27', outcome: if "Req Inc-1.b1.b27" is null then 'unresolved' else if "Req Inc-1.b1.b27" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b1.b28', outcome: if "Req Inc-1.b1.b28" is null then 'unresolved' else if "Req Inc-1.b1.b28" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b2.b1', outcome: if "Req Inc-1.b2.b1" is null then 'unresolved' else if "Req Inc-1.b2.b1" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b2.b2', outcome: if "Req Inc-1.b2.b2" is null then 'unresolved' else if "Req Inc-1.b2.b2" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b2.b3', outcome: if "Req Inc-1.b2.b3" is null then 'unresolved' else if "Req Inc-1.b2.b3" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b2.b4', outcome: if "Req Inc-1.b2.b4" is null then 'unresolved' else if "Req Inc-1.b2.b4" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b2.b5', outcome: if "Req Inc-1.b2.b5" is null then 'unresolved' else if "Req Inc-1.b2.b5" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b2.b6', outcome: if "Req Inc-1.b2.b6" is null then 'unresolved' else if "Req Inc-1.b2.b6" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b2.b7', outcome: if "Req Inc-1.b2.b7" is null then 'unresolved' else if "Req Inc-1.b2.b7" then 'satisfied' else 'violated' },
  Tuple { criterion: 'Inc-1.b2.b8', outcome: if "Req Inc-1.b2.b8" is null then 'unresolved' else if "Req Inc-1.b2.b8" then 'satisfied' else 'violated' } }

define "Any Requirement Violated":
  exists ("Requirement Outcomes" O where O.outcome = 'violated')
