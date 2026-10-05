import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { CircleHelp, Info, Scale } from 'lucide-react';
import SectionCard from '../components/SectionCard.jsx';
import insights from '../data/insights.json';

const humanLabels = {
  number_inpatient: 'Previous inpatient visits', number_emergency: 'Previous emergency visits', number_outpatient: 'Previous outpatient visits',
  num_medications: 'Medications during stay', number_diagnoses: 'Number of diagnoses', time_in_hospital: 'Length of hospital stay',
  num_lab_procedures: 'Laboratory procedures', num_procedures: 'Procedures during stay', age_midpoint: 'Age group',
  total_previous_visits: 'Total previous visits', has_previous_inpatient_visit: 'Any previous inpatient visit', total_procedures: 'Total procedures',
  discharge_disposition_id: 'Discharge disposition', admission_type_id: 'Admission type', admission_source_id: 'Admission source',
};

export default function RiskFactorsPage() {
  const data = insights.feature_importance.map((row) => ({ ...row, label: humanLabels[row.feature] || row.feature.replaceAll('_', ' ') }));
  return <>
    <div className="page-intro"><div><span className="eyebrow">MODEL INTERPRETATION</span><h2>Risk factors</h2><p>Features with the highest importance in the saved LightGBM model.</p></div><span className="source-chip"><Scale size={14} /> No model retraining</span></div>
    <div className="interpretation-callout"><Info size={18} /><p><strong>Feature importance is not a measure of clinical cause.</strong> A higher score means a feature contributed more to the fitted model’s predictions across its trees. It does not show that the feature causes readmission or how it changes risk for an individual.</p></div>
    <SectionCard title="Most influential model inputs" description="Gain-based importance aggregated to the original feature names from the saved final model.">
      <div className="importance-chart"><ResponsiveContainer width="100%" height={430}><BarChart data={data.slice().reverse()} layout="vertical" margin={{ top: 8, right: 30, left: 12, bottom: 0 }} barSize={19}><CartesianGrid horizontal={false} stroke="#e8eeea" /><XAxis type="number" tick={{ fill: '#87958d', fontSize: 11 }} axisLine={false} tickLine={false} /><YAxis type="category" dataKey="label" width={190} tick={{ fill: '#43594e', fontSize: 11 }} axisLine={false} tickLine={false} /><Tooltip formatter={(v)=>[Number(v).toLocaleString(),'Importance']} cursor={{ fill: '#f5f8f6' }} /><Bar dataKey="importance" fill="#328361" radius={[0,5,5,0]} /></BarChart></ResponsiveContainer></div>
      <div className="importance-table">{data.map((row,index)=><div key={row.feature}><span>{String(index+1).padStart(2,'0')}</span><strong>{row.label}</strong><div className="importance-track"><i style={{ width: `${Math.max(2, row.importance/data[0].importance*100)}%` }} /></div><b>{row.importance.toLocaleString()}</b></div>)}</div>
    </SectionCard>
    <SectionCard title="Interpretation notes" description="Context for reviewing feature importance."><div className="performance-notes"><div><CircleHelp size={17} /><div><strong>Relative contribution</strong><p>Importance values are relative within the fitted LightGBM model and depend on its training data and settings.</p></div></div><div><Scale size={17} /><div><strong>Not a causal ranking</strong><p>Correlated features can share or mask importance. This chart does not measure a treatment effect or clinical risk factor.</p></div></div></div></SectionCard>
    <p className="data-caveat">Source: saved outputs/final_model.joblib. The model was not retrained to create this view.</p>
  </>;
}
