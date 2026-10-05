export default function MetricCard({ label, value, note, icon: Icon, featured = false }) {
  return <article className={`metric-card ${featured ? 'metric-featured' : ''}`}>
    <div className="metric-top"><span>{label}</span>{Icon && <Icon size={17} />}</div>
    <div className="metric-number">{value}</div>
    {note && <div className="metric-note">{note}</div>}
  </article>;
}
