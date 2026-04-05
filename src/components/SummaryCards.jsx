export default function SummaryCards({ data }) {
  const valid = data.filter(r => r.peluang !== null)
  const high  = valid.filter(r => r.peluang >= 30).length
  const mid   = valid.filter(r => r.peluang >= 10 && r.peluang < 30).length
  const low   = valid.filter(r => r.peluang < 10).length

  return (
    <div id="summary-area" style={{ display: 'block' }}>
      <div className="summary-grid">
        <div className="stat-card total">
          <div className="stat-label">Total Prodi</div>
          <div className="stat-val">{valid.length}</div>
          <div className="stat-sub">dengan data peminat</div>
        </div>
        <div className="stat-card high">
          <div className="stat-label">Peluang Tinggi</div>
          <div className="stat-val">{high}</div>
          <div className="stat-sub">≥ 30%</div>
        </div>
        <div className="stat-card mid">
          <div className="stat-label">Peluang Sedang</div>
          <div className="stat-val">{mid}</div>
          <div className="stat-sub">10% – 30%</div>
        </div>
        <div className="stat-card low">
          <div className="stat-label">Peluang Ketat</div>
          <div className="stat-val">{low}</div>
          <div className="stat-sub">&lt; 10%</div>
        </div>
      </div>
    </div>
  )
}
