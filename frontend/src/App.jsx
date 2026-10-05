import { lazy, Suspense, useEffect, useMemo, useState } from 'react';
import React from "react";
import { Link, Route, Routes, useLocation } from 'react-router-dom';
import { CircleHelp, HeartPulse, Wifi, WifiOff } from 'lucide-react';
import Sidebar from './components/Sidebar.jsx';
import { getApiErrorMessage, getHealth, getModelInfo } from './services/api.js';

const Dashboard = lazy(() => import('./pages/Dashboard.jsx'));
const PredictPage = lazy(() => import('./pages/PredictPage.jsx'));
const InsightsPage = lazy(() => import('./pages/InsightsPage.jsx'));
const PerformancePage = lazy(() => import('./pages/PerformancePage.jsx'));
const RiskFactorsPage = lazy(() => import('./pages/RiskFactorsPage.jsx'));
const AboutPage = lazy(() => import('./pages/AboutPage.jsx'));

const pageNames = {
  '/': 'Dashboard', '/predict': 'Predict readmission', '/insights': 'Data insights',
  '/performance': 'Model performance', '/risk-factors': 'Risk factors', '/about': 'About this project',
};

export default function App() {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [apiStatus, setApiStatus] = useState('checking');
  const [modelInfo, setModelInfo] = useState(null);
  const [apiError, setApiError] = useState('');
  const currentTitle = useMemo(() => pageNames[location.pathname] || 'Dashboard', [location.pathname]);

  useEffect(() => {
    let active = true;
    Promise.all([getHealth(), getModelInfo()]).then(([, model]) => {
      if (active) { setApiStatus('online'); setModelInfo(model); setApiError(''); }
    }).catch((error) => {
      if (active) { setApiStatus('offline'); setApiError(getApiErrorMessage(error)); }
    });
    return () => { active = false; };
  }, []);

  return <div className="app-shell">
    <Sidebar open={sidebarOpen} onMenu={() => setSidebarOpen(true)} onClose={() => setSidebarOpen(false)} />
    <div className="main-column">
      <header className="topbar"><div className="topbar-left"><div className="breadcrumb"><span>Workspace</span><span className="breadcrumb-slash">/</span><strong>{currentTitle}</strong></div><div className="topbar-context">Diabetes Readmission Prediction</div></div>
        <div className="topbar-actions"><div className={`connection-status ${apiStatus}`}><span className="connection-indicator">{apiStatus === 'online' ? <Wifi size={14} /> : apiStatus === 'offline' ? <WifiOff size={14} /> : <span className="tiny-spinner" />}</span><span>{apiStatus === 'online' ? 'API connected' : apiStatus === 'checking' ? 'Connecting' : 'API unavailable'}</span></div><span className="topbar-divider" /><Link to="/about" className="icon-button help-button" aria-label="About this project"><CircleHelp size={18} /></Link><div className="user-chip"><div className="user-avatar"><HeartPulse size={16} /></div><div><strong>Academic workspace</strong><small>Read-only model</small></div></div></div>
      </header>
      <main className="page-content"><Suspense fallback={<div className="page-loading" role="status"><span className="tiny-spinner" /> Loading workspace</div>}><Routes>
        <Route path="/" element={<Dashboard modelInfo={modelInfo} apiStatus={apiStatus} apiError={apiStatus === 'offline' ? apiError : ''} />} />
        <Route path="/predict" element={<PredictPage />} />
        <Route path="/insights" element={<InsightsPage />} />
        <Route path="/performance" element={<PerformancePage modelInfo={modelInfo} />} />
        <Route path="/risk-factors" element={<RiskFactorsPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="*" element={<Dashboard modelInfo={modelInfo} apiStatus={apiStatus} apiError={apiStatus === 'offline' ? apiError : ''} />} />
      </Routes></Suspense>
      </main>
      <footer className="app-footer"><span>Diabetes Readmission Prediction <i>·</i> Academic decision support</span><span>Not for diagnosis or treatment decisions</span></footer>
    </div>
  </div>;
}
