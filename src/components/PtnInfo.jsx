export default function PtnInfo({ uni, meta }) {
  if (!uni || !meta) return null

  return (
    <div id="ptn-info" style={{ display: 'block' }}>
      <div className="ptn-title">{uni.nama}</div>
      <div className="ptn-meta">
        <div className="ptn-meta-item">
          📍 <span>{uni.kota} · {uni.provinsi}</span>
        </div>
        <div className="ptn-meta-item">
          🏛 <span>{meta.prodi_count ? `${meta.prodi_count} Program Studi` : '—'}</span>
        </div>
        {meta.web && (
          <div className="ptn-meta-item">
            🔗 <a
              href={meta.web}
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: 'var(--accent)', fontSize: '12px' }}
            >
              Website Resmi
            </a>
          </div>
        )}
      </div>
    </div>
  )
}
