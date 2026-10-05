import React from 'react';
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Award, CircleHelp, Crosshair, ShieldCheck } from 'lucide-react';
import SectionCard from '../components/SectionCard.jsx';
import MetricCard from '../components/MetricCard.jsx';
import comparisonCsv from '../../../outputs/model_comparison.csv?raw';

const modelData = comparisonCsv.trim().split(/\r?\n/).slice(1).map((line) => {
  const cells = line.split(',');
  return { model: cells[0], score: Number(cells[2]) };
});

export default function PerformancePage({ modelInfo }) {
  const cvScore = modelInfo?.cv_macro_f1 ?? modelData.find((row) => row.model === 'LightGBM')?.score ?? 0.4572;
  const testScore = modelInfo?.test_macro_f1 ?? 0.4581;
  return <>
    <div className="page-intro"><div><span className="eyebrow">EVALUATION</span><h2>Model performance</h2><p>Compare validation results and review the selected model’s held-out performance.</p></div><span className="source-chip"><ShieldCheck size={14} /> Model comparison results</span></div>
    <div className="metric-grid"><MetricCard label="Selected model" value={modelInfo?.model_name || 'LightGBM'} note="Chosen from five evaluated classifiers" icon={Award} featured /><MetricCard label="CV Macro-F1" value={Number(cvScore).toFixed(4)} note="5-fold grouped cross-validation" icon={Crosshair} /><MetricCard label="Test Macro-F1" value={Number(testScore).toFixed(4)} note="Held-out patient-level test set" icon={ShieldCheck} /></div>
    <SectionCard title="Cross-validation Macro-F1" description="Higher values indicate better balance across the three readmission classes. LightGBM is the selected final model.">
      <div className="performance-chart"><ResponsiveContainer width="100%" height={330}><BarChart data={modelData} layout="vertical" margin={{ top: 8, right: 38, left: 10, bottom: 3 }} barSize={27}><CartesianGrid horizontal={false} stroke="#e8eeea" /><XAxis type="number" domain={[0,0.5]} tickFormatter={(v)=>Number(v).toFixed(2)} tick={{ fill: '#87958d', fontSize: 11 }} axisLine={false} tickLine={false} /><YAxis type="category" dataKey="model" width={144} tick={{ fill: '#43594e', fontSize: 12, fontWeight: 600 }} axisLine={false} tickLine={false} /><Tooltip formatter={(v)=>[Number(v).toFixed(4),'CV Macro-F1']} cursor={{ fill: '#f5f8f6' }} /><Bar dataKey="score" radius={[0,5,5,0]}>{modelData.map((row)=><Cell key={row.model} fill={row.model==='LightGBM' ? '#23845b' : '#b9c9c0'} />)}</Bar></BarChart></ResponsiveContainer></div>
      <div className="chart-note"><span className="chart-legend-selected" /> Selected final model <span className="chart-legend-other" /> Other candidates <span className="chart-source">Source: outputs/model_comparison.csv</span></div>
    </SectionCard>
    <SectionCard title="How to read these scores" description="Macro-F1 gives each class equal weight when averaging precision and recall.">
      <div className="performance-notes"><div><CircleHelp size={17} /><div><strong>Cross-validation</strong><p>Five patient-grouped folds were used to estimate performance while keeping a patient’s encounters together.</p></div></div><div><ShieldCheck size={17} /><div><strong>Held-out evaluation</strong><p>The final test score was measured once on encounters set aside from model development.</p></div></div><div><Award size={17} /><div><strong>Selected model</strong><p>LightGBM achieved the highest tuned cross-validation Macro-F1 among the evaluated candidates.</p></div></div></div>
    </SectionCard>
    <p className="data-caveat">Evaluation results summarize this project’s dataset and experiment. They do not establish clinical effectiveness.</p>
  </>;
}
