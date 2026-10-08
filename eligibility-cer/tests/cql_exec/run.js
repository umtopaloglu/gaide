const cql = require('cql-execution'), cqlfhir = require('cql-exec-fhir'), fs = require('fs');
const lib = JSON.parse(fs.readFileSync(process.env.ELM_DIR + '/EligibilityCER_NCT06128837.json'));
const helpers = JSON.parse(fs.readFileSync(process.env.ELM_DIR + '/FHIRHelpers-4.0.0.json'));
const repo = new cql.Repository({ FHIRHelpers: helpers });
const ml = JSON.parse(fs.readFileSync(process.argv[2]));
function obs(code, display, extra, date, rr) {
  return { resource: { resourceType: 'Observation', id: 'o' + Math.random().toString(36).slice(2), status: 'final',
    code: { coding: [{ system: 'http://loinc.org', code, display }] }, effectiveDateTime: date, ...extra, ...(rr ? { referenceRange: [{ high: { value: rr } }] } : {}) } };
}
const q = (v, u) => ({ valueQuantity: { value: v, unit: u, system: 'http://unitsofmeasure.org', code: u } });
const P = ml.patient;
const entries = [{ resource: { resourceType: 'Patient', id: 'p1', birthDate: P.birthDate } }];
if (P.ecog != null) entries.push(obs('89247-1', 'ECOG', { valueInteger: P.ecog }, P.ecogDate));
const L = { ANC: ['751-8', '10*9/L'], Platelets: ['777-3', '10*9/L'], Hemoglobin: ['718-7', 'g/L'], 'Total bilirubin': ['1975-2', 'mg/dL'], AST: ['1920-8', 'U/L'], ALT: ['1742-6', 'U/L'], Albumin: ['1751-7', 'g/L'], Creatinine: ['2160-0', 'mg/dL'] };
for (const [k, v] of Object.entries(P.labs || {})) entries.push(obs(L[k][0], k, q(v.value, L[k][1]), v.date, v.uln));
const bundle = { resourceType: 'Bundle', type: 'collection', entry: entries };
const pr = new cqlfhir.PatientSource.FHIRv400(); pr.loadBundles([bundle]);
const exec = new cql.Executor(new cql.Library(lib, repo), new cql.CodeService({}), { ScreeningDate: cql.DateTime.parse('2026-10-06T00:00:00.0') });
exec.exec(pr).then(res => {
  const k = Object.keys(res.patientResults); if (!k.length) { console.log('NO PATIENTS'); process.exit(1); }
  const out = res.patientResults[k[0]]['Requirement Outcomes'];
  console.log(JSON.stringify(out.map(o => o.criterion + ':' + o.outcome)));
}).catch(e => { console.log('ERR', e.message); process.exit(1); });
