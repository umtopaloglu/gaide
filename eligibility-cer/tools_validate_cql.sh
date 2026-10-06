#!/usr/bin/env bash
# Validate generated CQL with the real CQL-to-ELM translator. Fails (non-zero) on ANY exception, error,
# or if no ELM is produced.  Optional 2nd arg: JSON  -> also emits ELM JSON (for cql-execution tests).
# Setup (once): mvn dependency:copy-dependencies for info.cqframework:cql-to-elm-cli 3.29.0 (+quick, engine)
#   into $CQL_LIB.  The translator bundles FHIRHelpers 4.0.0 / FHIR model 4.0.0, so the check runs against that
#   matching pair (our CQL declares 4.0.1; the constructs used are identical).
#   Usage: CQL_LIB=... tools_validate_cql.sh out/X.cql [JSON]     (ELM written to $ELM_OUT or a temp dir)
set -uo pipefail
: "${CQL_LIB:?set CQL_LIB to the directory of translator jars}"
fmt=${2:-XML}; ext=$(echo "$fmt" | tr 'A-Z' 'a-z')
work=$(mktemp -d); out=${ELM_OUT:-$work/elm}; mkdir -p "$out"
CP=$(ls "$CQL_LIB"/*.jar | grep -vE "model-jackson|elm-jackson" | tr '\n' ':')
for j in "$CQL_LIB"/*.jar; do unzip -o -q "$j" 'org/hl7/fhir/FHIRHelpers-4.0.0.cql' -d "$work/h" 2>/dev/null || true; done
cp "$work/h/org/hl7/fhir/FHIRHelpers-4.0.0.cql" "$work/"
b=$(basename "$1"); sed "s/'4.0.1'/'4.0.0'/g" "$1" > "$work/$b"
log=$(java -cp "$CP" org.cqframework.cql.cql2elm.cli.Main --input "$work" --output "$out" --format="$fmt" --signatures=Overloads 2>&1 | grep -v "Picked up")
rc=0
if echo "$log" | grep -qE "Exception|Error:|failed"; then echo "$log" | grep -E "Exception|Error:|failed" | sort | uniq -c | head -20; rc=1; fi
if [ ! -f "$out/${b%.cql}.$ext" ]; then echo "NO ELM PRODUCED for $b"; rc=1; fi
[ $rc -eq 0 ] && echo "translator OK: $b -> $out/${b%.cql}.$ext ($(echo "$log" | grep -c Warning) warnings)"
exit $rc
