import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, ArrowDownRight, ArrowRight, ArrowUpRight, BrainCircuit, Database, Sparkles } from 'lucide-react';
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';
import StatCard from '../components/StatCard.jsx';
import SectionCard from '../components/SectionCard.jsx';
import LoadingState from '../components/LoadingState.jsx';
import ErrorMessage from '../components/ErrorMessage.jsx';
import insights from '../data/insights.json';

const colors = { '<30': '#087f5b', '>30': '#4caf88', NO: '#cbd5d0' };
const outcomeText = { '<30': 'Readmitted within 30 days', '>30': 'Readmitted after 30 days', NO: 'Not readmitted' };

export default function Dashboard({ modelInfo, apiStatus, apiError }) {
  const navigate = useNavigate();
  const total = insights.records;
  const chartData = insights.readmission;
  return <>
    <section className="welcome-panel">
      <div className="welcome-copy"><span className="eyebrow">CLINICAL ANALYTICS · IT3051</span><h2>Diabetes Readmission Prediction</h2><p>Clinical decision-support analytics for estimating hospital readmission outcomes.</p>
        <button className="primary-button" onClick={() => navigate('/predict')}><Sparkles size={16} /> Predict Readmission <ArrowRight size={16} /></button>
      </div>
      <div className="welcome-visual" aria-hidden="true"><div className="welcome-orbit orbit-one" /><div className="welcome-orbit orbit-two" /><div className="welcome-heart"><Activity size={42} strokeWidth={1.5} /></div><div className="visual-tag tag-records"><span /> Encounter analysis</div><div className="visual-tag tag-model"><BrainCircuit size={14} /> LightGBM</div></div>
      <div className="welcome-bottom"><span className={`api-pill ${apiStatus === 'online' ? 'api-online' : ''}`}><span />{apiStatus === 'checking' ? 'Checking prediction service' : apiStatus === 'online' ? 'Prediction service connected' : 'Prediction service unavailable'}</span><span>Decision support for academic use</span></div>
    </section>
    {apiError && <ErrorMessage message={apiError} />}

    <div className="stats-grid">
      <StatCard icon={BrainCircuit} label="Final model" value={modelInfo?.model_name || 'LightGBM'} detail="Selected project classifier" />
      <StatCard icon={Activity} label="Task" value="Multiclass" detail={modelInfo?.task || 'Diabetes readmission prediction'} accent="blue" />
      <StatCard icon={Database} label="Outcomes" value={modelInfo?.class_labels?.length || 3} detail="<30 · >30 · NO" accent="violet" />
      <StatCard icon={Sparkles} label="Validation metric" value={modelInfo ? Number(modelInfo.cv_macro_f1).toFixed(4) : '—'} detail="CV Macro-F1" accent="gold" />
    </div>

    <div className="dashboard-grid">
      <SectionCard title="Readmission class distribution" description="The dataset includes three encounter outcomes." action={<button className="text-action" onClick={() => navigate('/insights')}>Explore data <ArrowRight size={14} /></button>}>
        <div className="distribution-layout"><div className="donut-wrap"><ResponsiveContainer width="100%" height={206}><PieChart><Pie data={chartData} dataKey="count" nameKey="readmitted" innerRadius={62} outerRadius={88} paddingAngle={3} stroke="none">{chartData.map((row) => <Cell key={row.readmitted} fill={colors[row.readmitted]} />)}</Pie><Tooltip formatter={(value) => [Number(value).toLocaleString(), 'Encounters']} /></PieChart></ResponsiveContainer><div className="donut-center"><strong>{(total / 1000).toFixed(1)}k</strong><span>encounters</span></div></div>
          <div className="distribution-list">{chartData.map((row) => <div className="distribution-row" key={row.readmitted}><span className="distribution-dot" style={{ backgroundColor: colors[row.readmitted] }} /><div><strong>{row.readmitted}</strong><small>{outcomeText[row.readmitted]}</small></div><div className="distribution-number"><strong>{row.percentage.toFixed(1)}%</strong><small>{row.count.toLocaleString()} records</small></div></div>)}</div></div>
      </SectionCard>
      <SectionCard title="Model snapshot" description="Performance for the selected LightGBM classifier.">
        {modelInfo ? <div className="snapshot-metrics"><div><span>Cross-validation Macro-F1</span><strong>{Number(modelInfo.cv_macro_f1).toFixed(4)}</strong><small>Average across five patient-grouped folds</small></div><div><span>Held-out test Macro-F1</span><strong>{Number(modelInfo.test_macro_f1).toFixed(4)}</strong><small>Reported on the untouched test set</small></div><button className="text-action" onClick={() => navigate('/performance')}>View model evaluation <ArrowRight size={14} /></button></div> : <LoadingState label="Loading model details" />}
      </SectionCard>
    </div>

    <SectionCard title="Understanding the three outcomes" description="The prediction describes the readmission class estimated by the model.">
      <div className="outcome-cards">{chartData.map((row) => <article className="outcome-card" key={row.readmitted}><div className="outcome-mark" style={{ color: row.readmitted === 'NO' ? '#5f6f67' : colors[row.readmitted], background: row.readmitted === 'NO' ? '#eef3f0' : `${colors[row.readmitted]}15` }}>{row.readmitted}</div><div><strong>{outcomeText[row.readmitted]}</strong><p>{row.readmitted === '<30' ? 'A subsequent readmission occurred within 30 days.' : row.readmitted === '>30' ? 'A subsequent readmission occurred after 30 days.' : 'No subsequent readmission was recorded.'}</p></div><span>{row.percentage.toFixed(1)}% of records</span></article>)}</div>
    </SectionCard>
    <div className="dashboard-footnote"><span><ArrowUpRight size={14} /> Dataset patterns are descriptive</span><span><ArrowDownRight size={14} /> Predictions are estimates, not clinical decisions</span></div>
  </>;
}
