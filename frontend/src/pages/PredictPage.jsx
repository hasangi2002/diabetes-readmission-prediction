import { useState } from 'react';
import { ArrowRight, Info, RotateCcw } from 'lucide-react';
import PredictionForm from '../components/PredictionForm.jsx';
import ResultCard from '../components/ResultCard.jsx';
import LoadingState from '../components/LoadingState.jsx';
import ErrorMessage from '../components/ErrorMessage.jsx';
import { getApiErrorMessage, getPrediction } from '../services/api.js';

export default function PredictPage() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [lastPayload, setLastPayload] = useState(null);
  const runPrediction = async (payload) => {
    setLoading(true); setError(''); setResult(null);
    try { setResult(await getPrediction(payload)); }
    catch (requestError) { setError(getApiErrorMessage(requestError)); }
    finally { setLoading(false); }
  };
  const submit = async (payload) => { setLastPayload(payload); await runPrediction(payload); };
  return <div className="predict-layout">
    <div className="predict-main">
      <div className="page-intro"><div><span className="eyebrow">MODEL-ASSISTED ESTIMATE</span><h2>Predict readmission</h2><p>Enter the encounter details below to see how the saved model scores each readmission outcome.</p></div><div className="step-chip"><span>01</span> Encounter details <ArrowRight size={13} /><span>02</span> Model estimate</div></div>
      <div className="gentle-warning"><Info size={17} /><p><strong>For academic and decision-support use.</strong> This tool does not provide a diagnosis or replace professional clinical judgment.</p></div>
      {error && <ErrorMessage message={error} onRetry={lastPayload ? () => runPrediction(lastPayload) : undefined} />}
      {loading && <LoadingState />}
      {result && <ResultCard result={result} />}
      <PredictionForm onSubmit={submit} loading={loading} />
      {result && <button className="reset-button" type="button" onClick={() => { setResult(null); setError(''); window.scrollTo({ top: 0, behavior: 'smooth' }); }}><RotateCcw size={15} /> Start another prediction</button>}
    </div>
    <aside className="predict-aside"><div className="aside-sticky"><div className="aside-heading"><span className="aside-icon"><Info size={18} /></span><div><strong>Before you begin</strong><small>Helpful guidance</small></div></div>
      <div className="aside-tip"><span>01</span><div><strong>Use encounter-level information</strong><p>Enter values recorded during the hospital stay and the year before it.</p></div></div>
      <div className="aside-tip"><span>02</span><div><strong>Choose “Not recorded” when needed</strong><p>Some demographic, payer, and diagnosis fields may be unavailable in the record.</p></div></div>
      <div className="aside-tip"><span>03</span><div><strong>Review all three scores</strong><p>The model returns a probability estimate for each outcome, not a certainty.</p></div></div>
      <div className="aside-divider" /><div className="aside-model"><span className="model-mini"><span /></span><div><strong>LightGBM model</strong><small>Saved and evaluated project model</small></div></div>
    </div></aside>
  </div>;
}
