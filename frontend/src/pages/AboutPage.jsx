import { Activity, BookOpenCheck, Database, HeartPulse, ShieldAlert } from 'lucide-react';
import SectionCard from '../components/SectionCard.jsx';

const items = [
  { icon: Database, title: 'Dataset', text: 'The project uses the UCI Diabetes 130-US Hospitals dataset, a historical collection of hospital encounters for patients with diabetes. It contains 101,766 records before the project’s exclusions and patient-level split.' },
  { icon: Activity, title: 'Prediction problem', text: 'For each encounter, the model estimates one of three recorded outcomes: readmitted within 30 days (<30), readmitted after 30 days (>30), or no readmission recorded (NO).' },
  { icon: HeartPulse, title: 'Final model', text: 'LightGBM was selected from five candidates. The saved model includes the project’s fitted scikit-learn preprocessing pipeline and is used without retraining at prediction time.' },
  { icon: BookOpenCheck, title: 'Evaluation approach', text: 'Candidate models were compared using five-fold stratified, patient-grouped cross-validation. Final results were calculated on a patient-level held-out test set.' },
  { icon: ShieldAlert, title: 'Limitations', text: 'The data is historical and may not represent current practice or other hospitals. A model estimate can reflect dataset biases, omit relevant context, and differ from a patient’s actual outcome. The displayed probabilities are not calibrated clinical risk estimates.' },
];

export default function AboutPage() {
  return <>
    <div className="page-intro"><div><span className="eyebrow">PROJECT OVERVIEW</span><h2>About this system</h2><p>A student-built academic project exploring hospital readmission classification.</p></div><span className="source-chip"><HeartPulse size={14} /> IT3051 · Fundamentals of Data Mining</span></div>
    <div className="about-hero"><div className="about-mark"><HeartPulse size={26} /></div><div><span className="eyebrow">DIABETES READMISSION PREDICTION</span><h3>Clinical Decision Support for Hospital Readmission Risk</h3><p>This interface connects a saved machine learning model with a clear way to review encounter patterns and compare outcome estimates.</p></div></div>
    <div className="about-grid">{items.map(({icon:Icon,title,text})=><SectionCard key={title} className="about-card"><div className="about-card-icon"><Icon size={18} /></div><h2>{title}</h2><p>{text}</p></SectionCard>)}</div>
    <div className="disclaimer-panel"><ShieldAlert size={19} /><div><strong>Healthcare disclaimer</strong><p>This is an academic decision-support system, not a medical diagnosis tool. Predictions are estimates and should not replace a qualified healthcare professional’s clinical judgment.</p></div></div>
  </>;
}
