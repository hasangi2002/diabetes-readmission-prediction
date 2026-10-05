import { NavLink } from 'react-router-dom';
import {
  Activity, BookOpen, ChartNoAxesCombined, ClipboardPlus,
  HeartPulse, LayoutDashboard, Menu, ShieldCheck, Stethoscope, X,
} from 'lucide-react';

const items = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/predict', label: 'Predict readmission', icon: ClipboardPlus },
  { to: '/insights', label: 'Data insights', icon: ChartNoAxesCombined },
  { to: '/performance', label: 'Model performance', icon: Activity },
  { to: '/risk-factors', label: 'Risk factors', icon: ShieldCheck },
  { to: '/about', label: 'About this project', icon: BookOpen },
];

export default function Sidebar({ open, onClose, onMenu }) {
  return <>
    <button className="mobile-menu" aria-label="Open navigation" onClick={onMenu}><Menu size={21} /></button>
    {open && <button className="sidebar-scrim" aria-label="Close navigation" onClick={onClose} />}
    <aside className={`sidebar ${open ? 'sidebar-open' : ''}`}>
      <div className="brand-lockup">
        <div className="brand-mark"><HeartPulse size={23} strokeWidth={2.2} /></div>
        <div><div className="brand-overline">CLINICAL ANALYTICS</div><div className="brand-name">Readmission<br />Decision Support</div></div>
        <button className="sidebar-close" aria-label="Close navigation" onClick={onClose}><X size={19} /></button>
      </div>
      <div className="nav-caption">WORKSPACE</div>
      <nav className="side-nav" aria-label="Main navigation">
        {items.map(({ to, label, icon: Icon, end }) => <NavLink key={to} to={to} end={end} onClick={onClose} className={({ isActive }) => `nav-item ${isActive ? 'nav-active' : ''}`}>
          <Icon size={18} strokeWidth={1.9} /><span>{label}</span>{label === 'Predict readmission' && <span className="nav-dot" />}
        </NavLink>)}
      </nav>
      <div className="sidebar-bottom">
        <div className="academic-note"><div className="note-icon"><Stethoscope size={16} /></div><div><strong>Academic project</strong><p>Decision support only.<br />Not a medical diagnosis.</p></div></div>
        <div className="sidebar-foot"><span className="sidebar-status-dot" /> Model service interface</div>
      </div>
    </aside>
  </>;
}
