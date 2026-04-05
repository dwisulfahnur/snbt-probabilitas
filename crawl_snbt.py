#!/usr/bin/env python3
"""
crawl_snbt.py — Crawl data prodi SNBT dari sidatagrun dan simpan ke data/{kode}.json
Jalankan: python crawl_snbt.py
Output  : folder data/ berisi satu JSON per PTN
"""

import json
import os
import re
import time
import sys

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://sidatagrun-public-1076756628210.asia-southeast2.run.app/ptn_sb.php"
DATA_DIR = "data"
DELAY    = 1.0  # detik antar request

UNIS = [
    {"kode": "1111", "nama": "UNIVERSITAS SYIAH KUALA"},
    {"kode": "1112", "nama": "UNIVERSITAS MALIKUSSALEH"},
    {"kode": "1113", "nama": "UNIVERSITAS TEUKU UMAR"},
    {"kode": "1114", "nama": "UNIVERSITAS SAMUDRA"},
    {"kode": "1115", "nama": "ISBI ACEH"},
    {"kode": "1121", "nama": "UNIVERSITAS SUMATERA UTARA"},
    {"kode": "1122", "nama": "UNIVERSITAS NEGERI MEDAN"},
    {"kode": "1131", "nama": "UNIVERSITAS RIAU"},
    {"kode": "1133", "nama": "UNIVERSITAS MARITIM RAJA ALI HAJI"},
    {"kode": "1141", "nama": "UNIVERSITAS ANDALAS"},
    {"kode": "1142", "nama": "UNIVERSITAS NEGERI PADANG"},
    {"kode": "1143", "nama": "ISI PADANG PANJANG"},
    {"kode": "1151", "nama": "UNIVERSITAS JAMBI"},
    {"kode": "1161", "nama": "UNIVERSITAS BENGKULU"},
    {"kode": "1171", "nama": "UNIVERSITAS SRIWIJAYA"},
    {"kode": "1181", "nama": "UNIVERSITAS BANGKA BELITUNG"},
    {"kode": "1191", "nama": "UNIVERSITAS LAMPUNG"},
    {"kode": "1192", "nama": "INSTITUT TEKNOLOGI SUMATERA"},
    {"kode": "1311", "nama": "UNIVERSITAS SULTAN AGENG TIRTAYASA"},
    {"kode": "1321", "nama": "UNIVERSITAS INDONESIA"},
    {"kode": "1323", "nama": "UNIVERSITAS NEGERI JAKARTA"},
    {"kode": "1324", "nama": "UPN \"VETERAN\" JAKARTA"},
    {"kode": "1331", "nama": "UNIVERSITAS SINGAPERBANGSA KARAWANG"},
    {"kode": "1332", "nama": "INSTITUT TEKNOLOGI BANDUNG"},
    {"kode": "1333", "nama": "UNIVERSITAS PADJADJARAN"},
    {"kode": "1334", "nama": "UNIVERSITAS PENDIDIKAN INDONESIA"},
    {"kode": "1335", "nama": "ISBI BANDUNG"},
    {"kode": "1341", "nama": "INSTITUT PERTANIAN BOGOR"},
    {"kode": "1342", "nama": "UNIVERSITAS SILIWANGI"},
    {"kode": "1351", "nama": "UNIVERSITAS JENDERAL SOEDIRMAN"},
    {"kode": "1352", "nama": "UNIVERSITAS TIDAR"},
    {"kode": "1353", "nama": "UNIVERSITAS SEBELAS MARET"},
    {"kode": "1354", "nama": "ISI SURAKARTA"},
    {"kode": "1355", "nama": "UNIVERSITAS DIPONEGORO"},
    {"kode": "1356", "nama": "UNIVERSITAS NEGERI SEMARANG"},
    {"kode": "1361", "nama": "UNIVERSITAS GADJAH MADA"},
    {"kode": "1362", "nama": "UNIVERSITAS NEGERI YOGYAKARTA"},
    {"kode": "1363", "nama": "UPN \"VETERAN\" YOGYAKARTA"},
    {"kode": "1364", "nama": "ISI YOGYAKARTA"},
    {"kode": "1371", "nama": "UNIVERSITAS JEMBER"},
    {"kode": "1372", "nama": "UNIVERSITAS BRAWIJAYA"},
    {"kode": "1373", "nama": "UNIVERSITAS NEGERI MALANG"},
    {"kode": "1381", "nama": "UNIVERSITAS AIRLANGGA"},
    {"kode": "1382", "nama": "INSTITUT TEKNOLOGI SEPULUH NOPEMBER"},
    {"kode": "1383", "nama": "UNIVERSITAS NEGERI SURABAYA"},
    {"kode": "1384", "nama": "UNIVERSITAS TRUNOJOYO MADURA"},
    {"kode": "1385", "nama": "UPN \"VETERAN\" JAWA TIMUR"},
    {"kode": "1511", "nama": "UNIVERSITAS TANJUNGPURA"},
    {"kode": "1521", "nama": "UNIVERSITAS PALANGKARAYA"},
    {"kode": "1531", "nama": "UNIVERSITAS LAMBUNG MANGKURAT"},
    {"kode": "1541", "nama": "UNIVERSITAS MULAWARMAN"},
    {"kode": "1542", "nama": "INSTITUT TEKNOLOGI KALIMANTAN"},
    {"kode": "1551", "nama": "UNIVERSITAS BORNEO TARAKAN"},
    {"kode": "1611", "nama": "UNIVERSITAS UDAYANA"},
    {"kode": "1612", "nama": "UNIVERSITAS PENDIDIKAN GANESHA"},
    {"kode": "1613", "nama": "ISI BALI"},
    {"kode": "1621", "nama": "UNIVERSITAS MATARAM"},
    {"kode": "1631", "nama": "UNIVERSITAS NUSA CENDANA"},
    {"kode": "1632", "nama": "UNIVERSITAS TIMOR"},
    {"kode": "1711", "nama": "UNIVERSITAS HASANUDDIN"},
    {"kode": "1712", "nama": "UNIVERSITAS NEGERI MAKASSAR"},
    {"kode": "1718", "nama": "INSTITUT TEKNOLOGI BJ. HABIBIE SULAWESI SELATAN"},
    {"kode": "1721", "nama": "UNIVERSITAS SAM RATULANGI"},
    {"kode": "1722", "nama": "UNIVERSITAS NEGERI MANADO"},
    {"kode": "1731", "nama": "UNIVERSITAS TADULAKO"},
    {"kode": "1741", "nama": "UNIVERSITAS SULAWESI BARAT"},
    {"kode": "1751", "nama": "UNIVERSITAS HALUOLEO"},
    {"kode": "1752", "nama": "UNIVERSITAS NEGERI GORONTALO"},
    {"kode": "1753", "nama": "UNIVERSITAS SEMBILAN BELAS NOVEMBER KOLAKA"},
    {"kode": "1811", "nama": "UNIVERSITAS PATTIMURA"},
    {"kode": "1821", "nama": "UNIVERSITAS KHAIRUN"},
    {"kode": "1911", "nama": "UNIVERSITAS CENDERAWASIH"},
    {"kode": "1912", "nama": "UNIVERSITAS MUSAMUS MERAUKE"},
    {"kode": "1913", "nama": "ISBI TANAH PAPUA"},
    {"kode": "1921", "nama": "UNIVERSITAS PAPUA"},
]


def parse_html(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    body_text = soup.get_text(" ", strip=True)

    prodi_count_m = re.search(r"Jumlah Prodi\s*:\s*(\d+)", body_text, re.I)
    web_m = re.search(r"Alamat Web\s*:\s*(https?://\S+)", body_text, re.I)

    # Ambil tabel terbesar
    tables = soup.find_all("table")
    best_rows = []
    for t in tables:
        rows = t.find_all("tr")
        if len(rows) > len(best_rows):
            best_rows = rows

    data = []
    for tr in best_rows:
        tds = tr.find_all("td")
        if len(tds) < 6:
            continue
        texts = [td.get_text(strip=True) for td in tds]
        if texts[0] in ("NO", "") or texts[2] in ("NAMA", ""):
            continue
        try:
            int(texts[0])
        except ValueError:
            continue

        def parse_int(s):
            s = re.sub(r"[^\d]", "", s)
            return int(s) if s else None

        tampung = parse_int(texts[4])
        peminat = parse_int(texts[5])
        peluang = round((tampung / peminat) * 100, 2) if (tampung and peminat) else None

        if texts[2] and len(texts[2]) > 1:
            data.append({
                "no":      texts[0],
                "kode":    texts[1],
                "nama":    texts[2],
                "jenjang": texts[3],
                "tampung": tampung,
                "peminat": peminat,
                "peluang": peluang,
            })

    return {
        "prodi_count": prodi_count_m.group(1) if prodi_count_m else None,
        "web":         web_m.group(1) if web_m else None,
        "data":        data,
    }


def crawl_ptn(kode: str, session: requests.Session) -> dict | None:
    # Parameter URL menggunakan 3 digit terakhir (drop digit pertama "1")
    ptn_param = kode[1:]
    url = f"{BASE_URL}?ptn={ptn_param}"
    try:
        res = session.get(url, timeout=15)
        res.raise_for_status()
        if len(res.text) < 500:
            print(f"  [SKIP] Konten terlalu pendek ({len(res.text)} chars)")
            return None
        return parse_html(res.text)
    except requests.RequestException as e:
        print(f"  [ERROR] {e}")
        return None


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    # Opsi: hanya crawl PTN yang belum ada file-nya (skip jika sudah)
    skip_existing = "--skip-existing" in sys.argv or "-s" in sys.argv

    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (compatible; snbt-crawler/1.0)"

    total = len(UNIS)
    ok = 0
    fail = 0

    for i, uni in enumerate(UNIS, 1):
        kode = uni["kode"]
        nama = uni["nama"]
        out_path = os.path.join(DATA_DIR, f"{kode}.json")

        if skip_existing and os.path.exists(out_path):
            print(f"[{i:2}/{total}] SKIP  {kode} — {nama}")
            ok += 1
            continue

        print(f"[{i:2}/{total}] Crawl {kode} — {nama} ...", end=" ", flush=True)
        result = crawl_ptn(kode, session)

        if result is None or len(result["data"]) == 0:
            print("GAGAL (tidak ada data)")
            fail += 1
        else:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, separators=(",", ":"))
            print(f"OK ({len(result['data'])} prodi)")
            ok += 1

        if i < total:
            time.sleep(DELAY)

    print(f"\nSelesai: {ok} berhasil, {fail} gagal. Data tersimpan di '{DATA_DIR}/'")


if __name__ == "__main__":
    main()
