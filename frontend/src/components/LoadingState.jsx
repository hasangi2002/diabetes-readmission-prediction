import { LoaderCircle } from 'lucide-react';

export default function LoadingState({ label = 'Generating prediction' }) {
  return <div className="loading-state" role="status" aria-live="polite"><LoaderCircle size={23} className="spin" /><div><strong>{label}</strong><span>Applying the saved model to this encounter.</span></div></div>;
}
