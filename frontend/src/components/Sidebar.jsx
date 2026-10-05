import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Activity, BookOpen, ChartNoAxesCombined, ClipboardPlus,
  HeartPulse, LayoutDashboard, Menu, ShieldCheck, Stethoscope, X,
} from 'lucide-react';

const workspaceItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/predict', label: 'Predict Readmission', icon: ClipboardPlus },
  { to: '/insights', label: 'Data Insights', icon: ChartNoAxesCombined },
  { to: '/performance', label: 'Model Performance', icon: Activity },
  { to: '/risk-factors', label: 'Risk Factors', icon: ShieldCheck },
];

const projectItems = [{ to: '/about', label: 'About this Project', icon: BookOpen }];

function NavigationItems({ items, onClose }) {
  return items.map(({ to, label, icon: Icon, end }) => <NavLink key={to} to={to} end={end} onClick={onClose} className={({ isActive }) => `nav-item ${isActive ? 'nav-active' : ''}`}>
    <Icon size={18} strokeWidth={1.9} /><span>{label}</span>{to === '/predict' && <span className="nav-dot" />}
  </NavLink>);
}

export default function Sidebar({ open, onClose, onMenu, apiStatus = 'checking' }) {
  return <>
    <button className="mobile-menu" aria-label="Open navigation" onClick={onMenu}><Menu size={21} /></button>
    {open && <button className="sidebar-scrim" aria-label="Close navigation" onClick={onClose} />}
    <aside className={`sidebar ${open ? 'sidebar-open' : ''}`}>
      <div className="brand-lockup">
        <div className="brand-mark"><HeartPulse size={23} strokeWidth={2.2} /></div>
        <div><div className="brand-overline">CLINICAL ANALYTICS</div><div className="brand-name">Diabetes Readmission<br />Decision Support</div></div>
        <button className="sidebar-close" aria-label="Close navigation" onClick={onClose}><X size={19} /></button>
      </div>
      <div className="nav-caption">WORKSPACE</div>
      <nav className="side-nav" aria-label="Main navigation"><NavigationItems items={workspaceItems} onClose={onClose} /></nav>
      <div className="nav-caption project-caption">PROJECT</div>
      <nav className="side-nav" aria-label="Project navigation"><NavigationItems items={projectItems} onClose={onClose} /></nav>
      <div className="sidebar-bottom">
        <div className="academic-note"><div className="note-icon"><Stethoscope size={16} /></div><div><strong>{apiStatus === 'online' ? 'Model service online' : apiStatus === 'offline' ? 'Model service unavailable' : 'Connecting to model service'}</strong><p>Academic decision support.<br />Not a medical diagnosis.</p></div></div>
        <div className="sidebar-foot"><span className={`sidebar-status-dot ${apiStatus}`} /> {apiStatus === 'online' ? 'API connected' : apiStatus === 'offline' ? 'API unavailable' : 'Checking service'}</div>
      </div>
    </aside>
  </>;
}
