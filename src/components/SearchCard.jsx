import { useState, useRef, useEffect } from 'react'
import { UNIS } from '../data/unis'

function highlight(text, q) {
  if (!q) return text
  const idx = text.toLowerCase().indexOf(q.toLowerCase())
  if (idx === -1) return text
  return (
    text.slice(0, idx) +
    '<mark>' + text.slice(idx, idx + q.length) + '</mark>' +
    text.slice(idx + q.length)
  )
}

function filterUnis(q) {
  const ql = q.toLowerCase()
  return UNIS.filter(u =>
    u.nama.toLowerCase().includes(ql) ||
    u.kode.includes(ql) ||
    u.kota.toLowerCase().includes(ql) ||
    u.provinsi.toLowerCase().includes(ql)
  )
}

function groupByProvinsi(unis) {
  return unis.reduce((acc, u) => {
    if (!acc[u.provinsi]) acc[u.provinsi] = []
    acc[u.provinsi].push(u)
    return acc
  }, {})
}

export default function SearchCard({ onLoad }) {
  const [query, setQuery]           = useState('')
  const [selected, setSelected]     = useState(null)
  const [isOpen, setIsOpen]         = useState(false)
  const [activeIdx, setActiveIdx]   = useState(-1)
  const [filtered, setFiltered]     = useState([])

  const wrapRef   = useRef(null)
  const inputRef  = useRef(null)
  const activeRef = useRef(null)

  // Scroll active item into view
  useEffect(() => {
    activeRef.current?.scrollIntoView({ block: 'nearest' })
  }, [activeIdx])

  // Close dropdown on outside click
  useEffect(() => {
    function handleOutsideClick(e) {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('click', handleOutsideClick)
    return () => document.removeEventListener('click', handleOutsideClick)
  }, [])

  function openWith(q) {
    const results = filterUnis(q)
    setFiltered(results)
    setIsOpen(true)
    setActiveIdx(-1)
  }

  function handleInputChange(e) {
    const q = e.target.value
    setQuery(q)
    if (selected && q !== selected.nama) setSelected(null)
    openWith(q)
  }

  function handleFocus() {
    if (!selected) openWith(query)
  }

  function handleKeyDown(e) {
    if (!isOpen) {
      if (e.key === 'ArrowDown' || e.key === 'Enter') openWith(query)
      return
    }
    if (e.key === 'ArrowDown') {
      setActiveIdx(i => Math.min(i + 1, filtered.length - 1))
    } else if (e.key === 'ArrowUp') {
      setActiveIdx(i => Math.max(i - 1, 0))
    } else if (e.key === 'Enter') {
      if (activeIdx >= 0 && filtered[activeIdx]) {
        selectUni(filtered[activeIdx])
      } else if (filtered.length === 1) {
        selectUni(filtered[0])
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false)
    }
  }

  function selectUni(uni) {
    setSelected(uni)
    setQuery(uni.nama)
    setIsOpen(false)
    setActiveIdx(-1)
  }

  function clearSelection() {
    setSelected(null)
    setQuery('')
    setIsOpen(false)
    setFiltered([])
    inputRef.current?.focus()
  }

  const groups = groupByProvinsi(filtered)

  return (
    <div className="search-card">
      <label className="search-label">Pilih Universitas</label>

      {/* Selected display */}
      {selected && (
        <div className="selected-uni show">
          <span className="selected-uni-kode">{selected.kode}</span>
          <div className="selected-uni-info">
            <div className="selected-uni-nama">{selected.nama}</div>
            <div className="selected-uni-loc">{selected.kota} · {selected.provinsi}</div>
          </div>
        </div>
      )}

      {/* Combobox */}
      <div className="combobox-wrap" ref={wrapRef}>
        <div className="combobox-input-row">
          <input
            ref={inputRef}
            className="combobox-input"
            type="text"
            placeholder="🔍  Ketik nama atau kode universitas..."
            autoComplete="off"
            spellCheck="false"
            value={query}
            onChange={handleInputChange}
            onFocus={handleFocus}
            onKeyDown={handleKeyDown}
          />
          {selected && (
            <button className="combobox-clear visible" onClick={clearSelection} title="Hapus pilihan">
              ✕
            </button>
          )}
        </div>

        {/* Dropdown */}
        {isOpen && (
          <div className="dropdown open">
            {filtered.length === 0 ? (
              <div className="dd-empty">Tidak ada universitas yang cocok.</div>
            ) : (
              Object.entries(groups).map(([prov, unis]) => (
                <div key={prov}>
                  <div className="dd-group-label">{prov}</div>
                  {unis.map(u => {
                    const flatIdx = filtered.indexOf(u)
                    const isActive   = flatIdx === activeIdx
                    const isSelected = u.kode === selected?.kode
                    return (
                      <div
                        key={u.kode}
                        ref={isActive ? activeRef : null}
                        className={`dd-item${isSelected ? ' selected' : ''}${isActive ? ' active' : ''}`}
                        onClick={() => selectUni(u)}
                      >
                        <span className="dd-kode">{u.kode}</span>
                        <div className="dd-info">
                          <div
                            className="dd-nama"
                            dangerouslySetInnerHTML={{ __html: highlight(u.nama, query) }}
                          />
                          <div className="dd-sub">{u.kota}</div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Load button */}
      <button
        id="btn-load"
        disabled={!selected}
        onClick={() => selected && onLoad(selected)}
      >
        {selected
          ? `Lihat Prodi ${selected.nama.split(' ').slice(0, 3).join(' ')} →`
          : 'Pilih universitas terlebih dahulu'
        }
      </button>
    </div>
  )
}
