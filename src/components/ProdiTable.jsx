import { useState } from 'react'

const SORT_FNS = {
  p_desc:       (a, b) => (b.peluang ?? -1)    - (a.peluang ?? -1),
  p_asc:        (a, b) => (a.peluang ?? 9999)  - (b.peluang ?? 9999),
  peminat_desc: (a, b) => (b.peminat ?? 0)     - (a.peminat ?? 0),
  peminat_asc:  (a, b) => (a.peminat ?? 9999)  - (b.peminat ?? 9999),
  tampung_desc: (a, b) => (b.tampung ?? 0)     - (a.tampung ?? 0),
  tampung_asc:  (a, b) => (a.tampung ?? 9999)  - (b.tampung ?? 9999),
  nama:         (a, b) => a.nama.localeCompare(b.nama, 'id'),
  nama_asc:     (a, b) => a.nama.localeCompare(b.nama, 'id'),
}

function badgeClass(p) {
  if (p === null) return 'badge-gray'
  if (p >= 30) return 'badge-green'
  if (p >= 10) return 'badge-amber'
  return 'badge-red'
}

function barColor(p) {
  if (p === null) return 'rgba(255,255,255,.1)'
  if (p >= 30) return 'var(--green)'
  if (p >= 10) return 'var(--amber)'
  return 'var(--red)'
}

function SortTh({ sortKey, currentSort, onSort, style, children }) {
  const base   = sortKey.replace(/_desc|_asc/, '')
  const active = currentSort.startsWith(base)
  const arrow  = !active ? '↕' : currentSort.endsWith('_asc') ? '↑' : '↓'

  return (
    <th className={active ? 'active' : ''} style={style} onClick={() => onSort(sortKey)}>
      {children} <span className="arr">{arrow}</span>
    </th>
  )
}

export default function ProdiTable({ data }) {
  const [searchQ, setSearchQ] = useState('')
  const [jenjang, setJenjang] = useState('')
  const [filter, setFilter]   = useState('')
  const [sort, setSort]       = useState('p_desc')

  function handleSort(key) {
    const full = key.includes('_') ? key : `${key}_desc`
    setSort(prev => prev === full ? full.replace('_desc', '_asc') : full)
  }

  const filtered = data
    .filter(r => {
      if (!r.nama.toLowerCase().includes(searchQ.toLowerCase())) return false
      if (jenjang && r.jenjang !== jenjang) return false
      if (filter === 'high' && (r.peluang === null || r.peluang < 30)) return false
      if (filter === 'mid'  && (r.peluang === null || r.peluang < 10 || r.peluang >= 30)) return false
      if (filter === 'low'  && (r.peluang === null || r.peluang >= 10)) return false
      return true
    })
    .sort(SORT_FNS[sort] || SORT_FNS.p_desc)

  const maxP = Math.max(...filtered.filter(r => r.peluang !== null).map(r => r.peluang), 1)

  const sortProps = { currentSort: sort, onSort: handleSort }

  return (
    <>
      {/* Controls */}
      <div id="controls-area" style={{ display: 'block' }}>
        <div className="controls-row">
          <input
            className="ctrl-search"
            type="text"
            placeholder="🔍  Cari nama prodi..."
            value={searchQ}
            onChange={e => setSearchQ(e.target.value)}
          />
          <select className="ctrl-select" value={jenjang} onChange={e => setJenjang(e.target.value)}>
            <option value="">Semua jenjang</option>
            <option value="Sarjana">S1 – Sarjana</option>
            <option value="Sarjana Terapan">D4 – Sarjana Terapan</option>
          </select>
          <select className="ctrl-select" value={filter} onChange={e => setFilter(e.target.value)}>
            <option value="">Semua peluang</option>
            <option value="high">Tinggi ≥30%</option>
            <option value="mid">Sedang 10–30%</option>
            <option value="low">Ketat &lt;10%</option>
          </select>
          <select className="ctrl-select" value={sort} onChange={e => setSort(e.target.value)}>
            <option value="p_desc">Peluang tertinggi</option>
            <option value="p_asc">Peluang terendah</option>
            <option value="peminat_desc">Peminat terbanyak</option>
            <option value="tampung_desc">Daya tampung terbesar</option>
            <option value="nama">Nama A–Z</option>
          </select>
          <span className="row-count">{filtered.length} prodi</span>
        </div>
      </div>

      {/* Table */}
      <div id="table-area" style={{ display: 'block' }}>
        <div className="tbl-wrap fade-in">
          <table>
            <thead>
              <tr>
                <SortTh sortKey="nama"         style={{ width: '36%' }} {...sortProps}>Nama Prodi</SortTh>
                <SortTh sortKey="tampung_desc" style={{ width: '8%'  }} {...sortProps}>Tampung</SortTh>
                <SortTh sortKey="peminat_desc" style={{ width: '9%'  }} {...sortProps}>Peminat</SortTh>
                <th style={{ width: '8%' }}>Jenjang</th>
                <SortTh sortKey="p_desc"       style={{ width: '12%' }} {...sortProps}>Peluang</SortTh>
                <th style={{ width: '27%' }}>Visualisasi</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={6}>
                    <div className="empty-state">Tidak ada prodi yang cocok.</div>
                  </td>
                </tr>
              ) : (
                filtered.map((r, i) => {
                  const pLabel = r.peluang !== null ? `${r.peluang.toFixed(1)}%` : 'N/A'
                  const barW   = r.peluang !== null
                    ? Math.min(100, (r.peluang / Math.max(maxP, 50)) * 100)
                    : 0

                  return (
                    <tr
                      key={r.kode}
                      style={{
                        animation: 'fadeIn .25s ease both',
                        animationDelay: `${Math.min(i, 15) * 0.02}s`,
                      }}
                    >
                      <td>
                        <div className="td-nama">{r.nama}</div>
                        <div className="td-kode">{r.kode}</div>
                      </td>
                      <td className={`td-num${r.tampung ? '' : ' td-num-muted'}`}>
                        {r.tampung ?? '—'}
                      </td>
                      <td className={`td-num${r.peminat ? '' : ' td-num-muted'}`}>
                        {r.peminat ? r.peminat.toLocaleString('id-ID') : '—'}
                      </td>
                      <td>
                        <span className={`badge ${r.jenjang === 'Sarjana Terapan' ? 'badge-d4' : 'badge-s1'}`}>
                          {r.jenjang === 'Sarjana Terapan' ? 'D4' : 'S1'}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${badgeClass(r.peluang)}`}>{pLabel}</span>
                      </td>
                      <td>
                        <div className="bar-wrap">
                          <div style={{
                            fontSize: '10px',
                            color: 'var(--text-dim)',
                            fontFamily: "'DM Mono', monospace",
                            textAlign: 'right',
                          }}>
                            {r.tampung ?? '—'} / {r.peminat ? r.peminat.toLocaleString('id-ID') : '—'}
                          </div>
                          <div className="bar-track">
                            <div
                              className="bar-fill"
                              style={{ width: `${barW.toFixed(1)}%`, background: barColor(r.peluang) }}
                            />
                          </div>
                        </div>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
        <p className="note">
          <strong>Cara baca:</strong> Peluang = Daya Tampung 2026 ÷ Peminat 2025 × 100%.
          Ini estimasi kasar berbasis rasio — semakin tinggi, semakin longgar persaingannya.
          Nilai UTBK tetap menjadi penentu utama kelulusan seleksi SNBT.
        </p>
      </div>
    </>
  )
}
