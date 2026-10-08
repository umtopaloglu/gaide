const cql = require('cql-execution'), cqlfhir = require('cql-exec-fhir'), fs = require('fs');
const D = process.argv[2];
const lib = JSON.parse(fs.readFileSync(D + '/EligibilityCER_NCT06838273_DRAFT.json'));
const repo = new cql.Repository({ FHIRHelpers: JSON.parse(fs.readFileSync(D + '/FHIRHelpers-4.0.0.json')) });
async function run(label, conds, coverage) {
  const entries = [{ resource: { resourceType: 'Patient', id: 'p', birthDate: '1960-01-01' } }];
  for (const c of conds) entries.push({ resource: { resourceType: 'Condition', id: 'c' + c, subject: { reference: 'Patient/p' },
    code: { coding: [{ system: 'http://snomed.info/sct', code: c }] } } });
  const pr = new cqlfhir.PatientSource.FHIRv400(); pr.loadBundles([{ resourceType: 'Bundle', type: 'collection', entry: entries }]);
  const params = { ScreeningDate: cql.DateTime.parse('2026-10-06T00:00:00.0') };
  if (coverage) params.ConditionCoverageComplete = true;
  const res = await new cql.Executor(new cql.Library(lib, repo), new cql.CodeService({}), params).exec(pr);
  const o = res.patientResults['p']['Requirement Outcomes'].find(x => x.criterion === 'Exc-22');
  console.log(label.padEnd(52), '->', o.outcome);
}
(async () => {
  await run('HIV recorded (coverage unknown)', ['86406008'], false);
  await run('no condition records, coverage UNKNOWN', [], false);
  await run('no condition records, site asserts coverage complete', [], true);
})();
