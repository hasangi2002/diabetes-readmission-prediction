export default function SectionCard({ title, description, action, children, className = '' }) {
  return <section className={`section-card ${className}`}>
    {(title || action) && <div className="section-card-head"><div>{title && <h2>{title}</h2>}{description && <p>{description}</p>}</div>{action}</div>}
    {children}
  </section>;
}
