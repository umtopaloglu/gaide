Differential check: execute the generated CQL in the `cql-execution` JS engine on synthetic FHIR patients.

    npm i cql-execution cql-exec-fhir                      # in this directory
    python ../../run.py cql NCT06128837 --allow-draft
    CQL_LIB=<translator jars> ELM_OUT=/tmp/elm ../../tools_validate_cql.sh ../../out/EligibilityCER_NCT06128837.cql JSON
    ELM_DIR=/tmp/elm node run.js p2.json                   # compare with: python ../../run.py evaluate ...

Expected (supported leaves agree with `cer/evaluate.py`): p2 -> Inc-6 violated (ECOG 3), Inc-9 violated (ANC 0.9);
p3 -> stale ECOG unresolved. p1's Inc-9 stays *unresolved* in CQL because the conditional-applicability threshold
("if liver metastases") is deliberately unsupported by the compiler (the Python evaluator resolves it from a fact).
