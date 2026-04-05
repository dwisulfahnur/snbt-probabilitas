import { useState } from 'react'
import SearchCard from './components/SearchCard'
import PtnInfo from './components/PtnInfo'
import SummaryCards from './components/SummaryCards'
import ProdiTable from './components/ProdiTable'

export default function App() {
  const [selectedUni, setSelectedUni] = useState(null)
  const [ptnMeta, setPtnMeta]         = useState(null)
  const [allData, setAllData]         = useState([])
  const [loading, setLoading]         = useState(false)
  const [error, setError]             = useState(null)

  async function handleLoad(uni) {
    setSelectedUni(uni)
    setError(null)
    setAllData([])
    setPtnMeta(null)
    setLoading(true)

    try {
      const res = await fetch(`/data/${uni.kode}.json`)
      if (!res.ok) {
        if (res.status === 404)
          throw new Error(`Data untuk PTN ini belum tersedia. Jalankan <code>python crawl_snbt.py</code> untuk mengunduh data.`)
        throw new Error(`HTTP ${res.status}`)
      }
      const json = await res.json()
      const data = json.data || []
      if (data.length === 0)
        throw new Error(`Tidak ada data prodi ditemukan untuk <strong>${uni.nama}</strong>.`)
      setPtnMeta({ prodi_count: json.prodi_count, web: json.web })
      setAllData(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const hasResults = !loading && allData.length > 0

  return (
    <div className="page">
      {/* Header */}
      <div className="header fade-in">
        <div className="header-badge">
          <span className="dot" />
          SNBT 2026 · Data Resmi Sidatagrun
        </div>
        <h1>Cek <em>Peluang</em> Masuk<br />Prodi PTN Impianmu</h1>
        <p className="subtitle">
          Pilih universitas untuk melihat estimasi peluang diterima berdasarkan
          daya tampung 2026 dan jumlah peminat 2025.
        </p>
      </div>

      {/* Search */}
      <div className="search-section fade-in" style={{ animationDelay: '.08s' }}>
        <SearchCard onLoad={handleLoad} />
      </div>

      {/* Error */}
      {error && (
        <div
          id="error-area"
          style={{ display: 'block' }}
          dangerouslySetInnerHTML={{ __html: `<strong>Gagal memuat data.</strong> ${error}` }}
        />
      )}

      {/* Loading */}
      {loading && (
        <div id="status-area" style={{ display: 'block' }}>
          <div className="spinner" />
          <div className="status-text">Mengambil data {selectedUni?.nama}...</div>
        </div>
      )}

      {/* Results */}
      {hasResults && (
        <>
          <PtnInfo uni={selectedUni} meta={ptnMeta} />
          <SummaryCards data={allData} />
          <ProdiTable data={allData} />
        </>
      )}
    </div>
  )
}
