import React from 'react';
import { AlertCircle, RotateCcw } from 'lucide-react';

export default function ErrorMessage({ message, onRetry }) {
  return <div className="error-message" role="alert"><AlertCircle size={19} /><div><strong>We couldn’t generate a prediction</strong><p>{message}</p>{onRetry && <button type="button" onClick={onRetry}><RotateCcw size={14} /> Try again</button>}</div></div>;
}
