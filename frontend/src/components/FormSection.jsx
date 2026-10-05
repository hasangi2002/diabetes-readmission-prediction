import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

export default function FormSection({ id, title, description, icon: Icon, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen);
  return <section className="form-section" id={id}>
    <button type="button" className="form-section-head" aria-expanded={open} onClick={() => setOpen((value) => !value)}>
      <span className="form-section-icon"><Icon size={19} /></span>
      <span className="form-section-title"><strong>{title}</strong><small>{description}</small></span>
      <ChevronDown size={19} className={`section-chevron ${open ? 'section-chevron-open' : ''}`} />
    </button>
    {open && <div className="form-section-content">{children}</div>}
  </section>;
}
