export default function StatCard({ icon: Icon, label, value, detail, accent = 'green' }) {
  return <article className="stat-card">
    <div className={`stat-icon stat-icon-${accent}`}><Icon size={19} strokeWidth={1.9} /></div>
    <div className="stat-label">{label}</div>
    <div className="stat-value">{value}</div>
    {detail && <div className="stat-detail">{detail}</div>}
  </article>;
}
