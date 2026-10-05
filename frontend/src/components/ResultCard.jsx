import React from 'react';
import { CheckCircle2, CircleHelp, Info, TrendingUp } from 'lucide-react';
import ProbabilityChart from './ProbabilityChart.jsx';

const tones = { '<30': 'early', '>30': 'later', NO: 'none' };

export default function ResultCard({ result }) {
  const tone = tones[result.predicted_class] || 'none';
  return <section className="result-card" aria-live="polite">
    <div className={`result-head result-${tone}`}>
      <div className="result-icon"><CheckCircle2 size={22} /></div>
      <div><span className="eyebrow">MODEL OUTPUT</span><h2>Predicted outcome</h2><p className="result-class">{result.predicted_class}</p><strong>{result.predicted_outcome}</strong></div>
      <div className="result-badge"><TrendingUp size={14} /> Highest model score</div>
    </div>
    <div className="result-body"><div className="result-chart-head"><div><h3>Probability distribution</h3><p>Scores across all three outcome classes</p></div><span className="prob-info"><CircleHelp size={15} /> Model estimates</span></div>
      <ProbabilityChart result={result} />
      <div className="result-disclaimer"><Info size={16} /><p>This prediction is intended for academic and decision-support purposes and should not replace professional clinical judgment.</p></div>
      <p className="probability-caveat">Probabilities are model estimates for the supplied encounter details, not a guarantee of an individual outcome.</p>
    </div>
  </section>;
}
