import { useMemo, useState } from 'react';
import {
  Activity, BedDouble, CalendarDays, ClipboardList, FlaskConical,
  Heart, Pill, Stethoscope,
} from 'lucide-react';
import FormSection from './FormSection.jsx';
import insights from '../data/insights.json';

const emptyForm = {
  race: '', gender: '', age: '', admission_type_id: '', discharge_disposition_id: '', admission_source_id: '',
  time_in_hospital: '', payer_code: '', medical_specialty: '', num_lab_procedures: '', num_procedures: '',
  num_medications: '', number_outpatient: '', number_emergency: '', number_inpatient: '', diag_1: '', diag_2: '', diag_3: '',
  number_diagnoses: '', max_glu_serum: '', A1Cresult: '', metformin: '', repaglinide: '', nateglinide: '',
  chlorpropamide: '', glimepiride: '', acetohexamide: '', glipizide: '', glyburide: '', tolbutamide: '',
  pioglitazone: '', rosiglitazone: '', acarbose: '', miglitol: '', troglitazone: '', tolazamide: '',
  examide: 'No', citoglipton: 'No', insulin: '', 'glyburide-metformin': '', 'glipizide-metformin': '',
  'glimepiride-pioglitazone': '', 'metformin-rosiglitazone': '', 'metformin-pioglitazone': '', change: '', diabetesMed: '',
};

const medNames = {
  metformin: 'Metformin', repaglinide: 'Repaglinide', nateglinide: 'Nateglinide', chlorpropamide: 'Chlorpropamide',
  glimepiride: 'Glimepiride', acetohexamide: 'Acetohexamide', glipizide: 'Glipizide', glyburide: 'Glyburide',
  tolbutamide: 'Tolbutamide', pioglitazone: 'Pioglitazone', rosiglitazone: 'Rosiglitazone', acarbose: 'Acarbose',
  miglitol: 'Miglitol', troglitazone: 'Troglitazone', tolazamide: 'Tolazamide', insulin: 'Insulin',
  'glyburide-metformin': 'Glyburide + metformin', 'glipizide-metformin': 'Glipizide + metformin',
  'glimepiride-pioglitazone': 'Glimepiride + pioglitazone', 'metformin-rosiglitazone': 'Metformin + rosiglitazone',
  'metformin-pioglitazone': 'Metformin + pioglitazone',
};

function SelectField({ name, label, value, onChange, options, hint, required = true }) {
  return <label className="field-wrap" htmlFor={name}>
    <span className="field-label">{label}{required && <span className="required-mark">*</span>}{hint && <span className="field-hint" title={hint} aria-label={hint}>i</span>}</span>
    <select id={name} name={name} value={value} onChange={onChange} required={required}>
      <option value="">Select an option</option>
      {options.map((option) => typeof option === 'string'
        ? <option key={option} value={option}>{option === '?' ? 'Not recorded' : option}</option>
        : <option key={option.value} value={option.value}>{option.label}</option>)}
    </select>
  </label>;
}

function NumberField({ name, label, value, onChange, min, max, hint, required = true }) {
  return <label className="field-wrap" htmlFor={name}>
    <span className="field-label">{label}{required && <span className="required-mark">*</span>}{hint && <span className="field-hint" title={hint} aria-label={hint}>i</span>}</span>
    <input id={name} name={name} type="number" min={min} max={max} step="1" inputMode="numeric" value={value} onChange={onChange} required={required} />
    {max > 25 && <small className="range-hint">Enter a whole number from {min} to {max}</small>}
  </label>;
}

const codes = (max) => Array.from({ length: max }, (_, i) => ({ value: i + 1, label: `Category ${String(i + 1).padStart(2, '0')}` }));
const changeOptions = ['No', 'Ch', '?'];
const medicationOptions = ['No', 'Steady', 'Up', 'Down', '?'];
const limitedMedicationOptions = {
  acetohexamide: ['No', 'Steady', '?'], tolbutamide: ['No', 'Steady', '?'],
  troglitazone: ['No', 'Steady', '?'], tolazamide: ['No', 'Steady', 'Up', '?'],
  'glipizide-metformin': ['No', 'Steady', '?'], 'glimepiride-pioglitazone': ['No', 'Steady', '?'],
  'metformin-rosiglitazone': ['No', 'Steady', '?'], 'metformin-pioglitazone': ['No', 'Steady', '?'],
};
const labs = ['None', '>300', 'Norm', '>200', '?'];
const ages = Array.from({ length: 10 }, (_, i) => `[${i * 10}-${(i + 1) * 10})`);
const integerFields = [
  'admission_type_id', 'discharge_disposition_id', 'admission_source_id', 'time_in_hospital',
  'num_lab_procedures', 'num_procedures', 'num_medications', 'number_outpatient', 'number_emergency',
  'number_inpatient', 'number_diagnoses',
];

export default function PredictionForm({ onSubmit, loading }) {
  const [form, setForm] = useState(emptyForm);
  const [formError, setFormError] = useState('');
  const diagnosisOptions = useMemo(() => insights.diagnoses.map((code) => <option key={code} value={code} />), []);
  const update = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }));

  const submit = async (event) => {
    event.preventDefault();
    setFormError('');
    const currentForm = event.currentTarget;
    if (!currentForm.reportValidity()) return;
    for (const name of integerFields) {
      if (!Number.isInteger(Number(form[name]))) {
        setFormError('Please enter whole numbers for all count and admission fields.');
        document.getElementById(name)?.focus();
        return;
      }
    }
    const payload = { ...form };
    integerFields.forEach((name) => { payload[name] = Number(payload[name]); });
    try { await onSubmit(payload); }
    catch { /* The page renders the service error state. */ }
  };

  return <form className="prediction-form" onSubmit={submit} noValidate>
    <div className="form-intro"><div><span className="eyebrow">ENCOUNTER ASSESSMENT</span><h2>Enter patient and visit details</h2><p>Use the information recorded for the hospital encounter. Fields marked <b>*</b> are required.</p></div><div className="form-completion"><span>REQUIRED DATA</span><strong>Clinical encounter</strong></div></div>

    <FormSection title="Patient information" description="Basic demographic details" icon={Heart}>
      <div className="form-grid three-col">
        <SelectField name="race" label="Race / ethnicity" value={form.race} onChange={update} options={['Caucasian', 'AfricanAmerican', 'Asian', 'Hispanic', 'Other', '?']} />
        <SelectField name="gender" label="Gender" value={form.gender} onChange={update} options={['Female', 'Male', 'Unknown/Invalid', '?']} />
        <SelectField name="age" label="Age range" hint="Age is grouped into ten-year bands in the study dataset." value={form.age} onChange={update} options={ages} />
      </div>
    </FormSection>

    <FormSection title="Hospital admission" description="How and where the encounter began and ended" icon={BedDouble}>
      <div className="form-grid three-col">
        <SelectField name="admission_type_id" label="Admission type" value={form.admission_type_id} onChange={update} options={codes(8)} hint="Choose the recorded admission category." />
        <SelectField name="discharge_disposition_id" label="Discharge disposition" value={form.discharge_disposition_id} onChange={update} options={codes(28)} hint="Choose the discharge category recorded for this encounter." />
        <SelectField name="admission_source_id" label="Admission source" value={form.admission_source_id} onChange={update} options={codes(25)} hint="Choose where the patient was referred from." />
        <NumberField name="time_in_hospital" label="Length of stay (days)" min={1} max={14} value={form.time_in_hospital} onChange={update} />
        <SelectField name="payer_code" label="Insurance / payer" value={form.payer_code} onChange={update} options={['MC', 'MD', 'HM', 'UN', 'BC', 'SP', 'CP', 'SI', 'DM', 'CM', 'CH', 'PO', 'WC', 'OT', 'OG', 'MP', 'FR', '?']} hint="Select the payer code recorded in the encounter." />
        <SelectField name="medical_specialty" label="Admitting specialty" value={form.medical_specialty} onChange={update} options={[...insights.specialties, '?']} hint="The specialty of the physician associated with the encounter." />
      </div>
    </FormSection>

    <FormSection title="Healthcare utilization" description="Recent care use and services during this visit" icon={Activity}>
      <div className="form-grid three-col">
        <NumberField name="number_outpatient" label="Previous outpatient visits" min={0} max={42} value={form.number_outpatient} onChange={update} hint="Visits in the year before this encounter." />
        <NumberField name="number_emergency" label="Previous emergency visits" min={0} max={76} value={form.number_emergency} onChange={update} hint="Visits in the year before this encounter." />
        <NumberField name="number_inpatient" label="Previous inpatient visits" min={0} max={21} value={form.number_inpatient} onChange={update} hint="Inpatient visits in the year before this encounter." />
        <NumberField name="num_medications" label="Medications during stay" min={0} max={81} value={form.num_medications} onChange={update} />
        <NumberField name="num_procedures" label="Procedures during stay" min={0} max={6} value={form.num_procedures} onChange={update} />
        <NumberField name="number_diagnoses" label="Diagnoses recorded" min={1} max={16} value={form.number_diagnoses} onChange={update} />
      </div>
    </FormSection>

    <FormSection title="Clinical information" description="Primary and secondary diagnosis codes" icon={Stethoscope}>
      <p className="section-help">Search for an ICD-9 code from the study dataset. Use “Not recorded” when a code is unavailable.</p>
      <div className="form-grid three-col">
        {['diag_1', 'diag_2', 'diag_3'].map((name, i) => <label className="field-wrap" htmlFor={name} key={name}>
          <span className="field-label">{['Primary diagnosis', 'Secondary diagnosis', 'Additional diagnosis'][i]}<span className="required-mark">*</span><span className="field-hint" title="ICD-9 diagnosis code">i</span></span>
          <input list={`${name}-codes`} id={name} name={name} value={form[name]} onChange={update} required maxLength={10} pattern="(?:[VE][0-9]{2,3}(?:\.[0-9]{1,2})?|[0-9]{1,3}(?:\.[0-9]{1,2})?|\?)" placeholder="Search or type a code" />
          <datalist id={`${name}-codes`}><option value="?">Not recorded</option>{diagnosisOptions}</datalist>
        </label>)}
      </div>
    </FormSection>

    <FormSection title="Laboratory information" description="Testing and laboratory procedures during the stay" icon={FlaskConical}>
      <div className="form-grid three-col">
        <NumberField name="num_lab_procedures" label="Laboratory procedures" min={0} max={132} value={form.num_lab_procedures} onChange={update} />
        <SelectField name="max_glu_serum" label="Highest glucose result" hint="Select the result category, or None if not tested." value={form.max_glu_serum} onChange={update} options={labs} />
        <SelectField name="A1Cresult" label="HbA1c result" hint="Select the result category, or None if not tested." value={form.A1Cresult} onChange={update} options={['None', '>7', '>8', 'Norm', '?']} />
      </div>
    </FormSection>

    <FormSection title="Diabetes medication" description="Medication changes and prescribed diabetes therapies" icon={Pill}>
      <div className="form-grid three-col">
        <SelectField name="change" label="Medication changed during stay" hint="Indicates whether a diabetes medication dose or type changed." value={form.change} onChange={update} options={changeOptions} />
        <SelectField name="diabetesMed" label="Diabetes medication prescribed" value={form.diabetesMed} onChange={update} options={['Yes', 'No', '?']} />
        {Object.entries(medNames).map(([name, label]) => <SelectField key={name} name={name} label={label} value={form[name]} onChange={update} options={limitedMedicationOptions[name] || medicationOptions} />)}
      </div>
      <p className="medication-note"><CalendarDays size={15} />Choose the status recorded for this encounter: no use, unchanged dose, dose increased, or dose decreased.</p>
    </FormSection>

    <div className="form-submit-row"><span><span className="required-mark">*</span> Required field</span><button className="primary-button" type="submit" disabled={loading}><ClipboardList size={17} />{loading ? 'Generating…' : 'Generate prediction'}</button></div>
    {formError && <p className="inline-error" role="alert">{formError}</p>}
  </form>;
}
