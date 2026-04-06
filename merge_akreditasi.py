#!/usr/bin/env python3
"""
merge_akreditasi.py — Merge akreditasi BAN-PT ke data prodi SNBT.
Buat file akreditasi_merged.json per PTN di public/data/.

Mapping approach:
1. Match berdasarkan nama institusi (75/75 PTN berhasil di-map)
2. Match prodi berdasarkan (nama_normalized, jenjang_normalized)
3. Fuzzy fallback: partial match, word overlap

Output: public/data/{kode}_akreditasi.json
"""

import json
import re
import os
import glob
from collections import defaultdict

AKRED_PATH = "akreditasi.json"
DATA_DIR = "public/data"
OUTPUT_DIR = "public/data"

# ===================================================================
# NAME MAP: kode SNBT -> nama institusi di akreditasi.json
# ===================================================================
NAME_MAP = {
    "1111": "UNIVERSITAS SYIAH KUALA",
    "1112": "UNIVERSITAS MALIKUSSALEH",
    "1113": "UNIVERSITAS TEUKU UMAR",
    "1114": "UNIVERSITAS SAMUDRA",
    "1115": "INSTITUT SENI BUDAYA INDONESIA ACEH",
    "1121": "UNIVERSITAS SUMATERA UTARA",
    "1122": "UNIVERSITAS NEGERI MEDAN",
    "1131": "UNIVERSITAS RIAU",
    "1133": "UNIVERSITAS MARITIM RAJA ALI HAJI",
    "1141": "UNIVERSITAS ANDALAS",
    "1142": "UNIVERSITAS NEGERI PADANG",
    "1143": "INSTITUT SENI INDONESIA PADANG PANJANG",
    "1151": "UNIVERSITAS JAMBI",
    "1161": "UNIVERSITAS BENGKULU",
    "1171": "UNIVERSITAS SRIWIJAYA",
    "1181": "UNIVERSITAS BANGKA BELITUNG",
    "1191": "UNIVERSITAS LAMPUNG",
    "1192": "INSTITUT TEKNOLOGI SUMATERA",
    "1311": "UNIVERSITAS SULTAN AGENG TIRTAYASA",
    "1321": "UNIVERSITAS INDONESIA",
    "1323": "UNIVERSITAS NEGERI JAKARTA",
    "1324": "UNIVERSITAS PEMBANGUNAN NASIONAL VETERAN JAKARTA",
    "1331": "UNIVERSITAS SINGAPERBANGSA KARAWANG",
    "1332": "INSTITUT TEKNOLOGI BANDUNG",
    "1333": "UNIVERSITAS PADJADJARAN",
    "1334": "UNIVERSITAS PENDIDIKAN INDONESIA",
    "1335": "INSTITUT SENI BUDAYA INDONESIA BANDUNG",
    "1341": "INSTITUT PERTANIAN BOGOR",
    "1342": "UNIVERSITAS SILIWANGI",
    "1351": "UNIVERSITAS JENDERAL SOEDIRMAN",
    "1352": "UNIVERSITAS TIDAR",
    "1353": "UNIVERSITAS SEBELAS MARET",
    "1354": "INSTITUT SENI INDONESIA SURAKARTA",
    "1355": "UNIVERSITAS DIPONEGORO",
    "1356": "UNIVERSITAS NEGERI SEMARANG",
    "1361": "UNIVERSITAS GADJAH MADA",
    "1362": "UNIVERSITAS NEGERI YOGYAKARTA",
    "1363": "UNIVERSITAS PEMBANGUNAN NASIONAL VETERAN YOGYAKARTA",
    "1364": "INSTITUT SENI INDONESIA YOGYAKARTA",
    "1371": "UNIVERSITAS JEMBER",
    "1372": "UNIVERSITAS BRAWIJAYA",
    "1373": "UNIVERSITAS NEGERI MALANG",
    "1381": "UNIVERSITAS AIRLANGGA",
    "1382": "INSTITUT TEKNOLOGI SEPULUH NOPEMBER",
    "1383": "UNIVERSITAS NEGERI SURABAYA",
    "1384": "Universitas Trunojoyo",
    "1385": "UNIVERSITAS PEMBANGUNAN NASIONAL VETERAN JAWA TIMUR",
    "1511": "UNIVERSITAS TANJUNGPURA",
    "1521": "UNIVERSITAS PALANGKA RAYA",
    "1531": "UNIVERSITAS LAMBUNG MANGKURAT",
    "1541": "UNIVERSITAS MULAWARMAN",
    "1542": "INSTITUT TEKNOLOGI KALIMANTAN",
    "1551": "UNIVERSITAS BORNEO TARAKAN",
    "1611": "UNIVERSITAS UDAYANA",
    "1612": "UNIVERSITAS PENDIDIKAN GANESHA",
    "1613": "INSTITUT SENI INDONESIA DENPASAR",
    "1621": "UNIVERSITAS MATARAM",
    "1631": "UNIVERSITAS NUSA CENDANA",
    "1632": "UNIVERSITAS TIMOR",
    "1711": "UNIVERSITAS HASANUDDIN",
    "1712": "UNIVERSITAS NEGERI MAKASSAR",
    "1718": "INSTITUT TEKNOLOGI BACHARUDDIN JUSUF HABIBIE",
    "1721": "UNIVERSITAS SAM RATULANGI",
    "1722": "UNIVERSITAS NEGERI MANADO",
    "1731": "UNIVERSITAS TADULAKO",
    "1741": "UNIVERSITAS SULAWESI BARAT",
    "1751": "UNIVERSITAS HALU OLEO",
    "1752": "UNIVERSITAS NEGERI GORONTALO",
    "1753": "UNIVERSITAS SEMBILANBELAS NOVEMBER KOLAKA",
    "1811": "UNIVERSITAS PATTIMURA",
    "1821": "UNIVERSITAS KHAIRUN",
    "1911": "UNIVERSITAS CENDERAWASIH",
    "1912": "UNIVERSITAS MUSAMUS MERAUKE",
    "1913": "INSTITUT SENI BUDAYA INDONESIA TANAH PAPUA",
    "1921": "UNIVERSITAS PAPUA",

    # =====================================================================
    # PTN VOKASI — UIN / IAIN (exact name from akreditasi.json)
    # =====================================================================
    "1116": "Universitas Islam Negeri Ar-Raniry Banda Aceh",
    "1123": "Universitas Islam Negeri Sumatera Utara Medan",
    "1124": "Universitas Islam Negeri Syekh Ali Hasan Ahmad Addary Padangsidimpuan",
    "1132": "Universitas Islam Negeri Sultan Syarif Kasim Riau",
    "1144": "Universitas Islam Negeri Imam Bonjol Padang",
    "1152": "Universitas Islam Negeri Sultan Thaha Saifuddin Jambi",
    "1172": "Universitas Islam Negeri Raden Fatah Palembang",
    "1193": "Universitas Islam Negeri Raden Intan Lampung",
    "1194": "Institut Agama Islam Negeri Mahmud Yunus Batusangkar",
    "1195": "Universitas Islam Negeri Sjech M. Djamil Djambek Bukittinggi",
    "1312": "Universitas Islam Negeri Sultan Maulana Hasanuddin Banten",
    "1322": "Universitas Islam Negeri Syarif Hidayatullah",
    "1336": "Universitas Islam Negeri Sunan Gunung Djati Bandung",
    "1357": "Universitas Islam Negeri Walisongo Semarang",
    "1358": "Universitas Islam Negeri Raden Mas Said Surakarta",
    "1365": "Universitas Islam Negeri Sunan Kalijaga Yogyakarta",
    "1366": "Universitas Islam Negeri Profesor Kiai Haji Saifuddin Zuhri Purwokerto",
    "1367": "Institut Agama Islam Negeri Salatiga",
    "1368": "Universitas Islam Negeri K.H. Abdurrahman Wahid Pekalongan",
    "1374": "Universitas Islam Negeri Maulana Malik Ibrahim Malang",
    "1386": "Universitas Islam Negeri Sunan Ampel Surabaya",
    "1532": "Universitas Islam Negeri Antasari Banjarmasin",
    "1571": "Universitas Islam Negeri Sultan Aji Muhammad Idris Samarinda",
    "1622": "Universitas Islam Negeri Mataram",
    "1713": "Universitas Islam Negeri Alauddin Makassar",
    "1732": "UIN Datokarama Palu",

    # =====================================================================
    # PTKIN — Politeknik Negeri (nama di akreditasi.json tanpa suffix lokasi)
    # =====================================================================
    "2221": "POLITEKNIK NEGERI LHOKSEUMAWE",
    "2222": "POLITEKNIK NEGERI MEDAN",
    "2231": "POLITEKNIK NEGERI BATAM",
    "2232": "POLITEKNIK NEGERI BENGKALIS",
    "2241": "POLITEKNIK NEGERI PADANG",
    "2242": "POLITEKNIK PERTANIAN NEGERI PAYAKUMBUH",
    "2271": "POLITEKNIK NEGERI SRIWIJAYA",
    "2281": "POLITEKNIK MANUFAKTUR NEGERI BANGKA BELITUNG",
    "2291": "POLITEKNIK NEGERI LAMPUNG",
    "2421": "POLITEKNIK NEGERI JAKARTA",
    "2422": "POLITEKNIK NEGERI MEDIA KREATIF",
    "2431": "POLITEKNIK NEGERI BANDUNG",
    "2432": "POLITEKNIK MANUFAKTUR BANDUNG",
    "2433": "POLITEKNIK NEGERI INDRAMAYU",
    "2434": "POLITEKNIK NEGERI SUBANG",
    "2452": "POLITEKNIK NEGERI SEMARANG",
    # =====================================================================
    # PTKIN — Politeknik Negeri (nama di akreditasi.json, Title Case, no suffix)
    # =====================================================================
    "2221": "Politeknik Negeri Lhokseumawe",
    "2222": "Politeknik Negeri Medan",
    "2231": "Politeknik Negeri Batam",
    "2232": "Politeknik Negeri Bengkalis",
    "2241": "Politeknik Negeri Padang",
    "2242": "Politeknik Pertanian Negeri Payakumbuh",
    "2271": "Politeknik Negeri Sriwijaya",
    "2281": "Politeknik Manufaktur Negeri Bangka Belitung",
    "2291": "Politeknik Negeri Lampung",
    "2421": "Politeknik Negeri Jakarta",
    "2422": "Politeknik Negeri Media Kreatif",
    "2431": "Politeknik Negeri Bandung",
    "2432": "Politeknik Manufaktur Bandung",
    "2433": "Politeknik Negeri Indramayu",
    "2434": "Politeknik Negeri Subang",
    "2452": "Politeknik Negeri Semarang",
    "2453": "Politeknik Negeri Cilacap",
    "2454": "Politeknik Maritim Negeri Indonesia",
    "2471": "Politeknik Negeri Banyuwangi",
    "2472": "Politeknik Negeri Jember",
    "2473": "Politeknik Negeri Madiun",
    "2474": "Politeknik Negeri Malang",
    "2481": "Politeknik Perkapalan Negeri Surabaya",
    "2482": "Politeknik Elektronika Negeri Surabaya",
    "2483": "Politeknik Negeri Madura",
    "2515": "Politeknik Negeri Pontianak",
    "2516": "Politeknik Negeri Ketapang",
    "2517": "Politeknik Negeri Sambas",
    "2536": "Politeknik Negeri Banjarmasin",
    "2537": "Politeknik Negeri Tanah Laut",
    "2552": "Politeknik Negeri Nunukan",
    "2561": "Politeknik Pertanian Negeri Samarinda",
    "2562": "Politeknik Negeri Samarinda",
    "2563": "Politeknik Negeri Balikpapan",
    "2617": "Politeknik Negeri Bali",
    "2641": "Politeknik Negeri Kupang",
    "2642": "Politeknik Pertanian Negeri Kupang",
    "2716": "Politeknik Negeri Ujung Pandang",
    "2717": "Politeknik Pertanian Negeri Pangkajene Kepulauan",
    "2727": "Politeknik Negeri Manado",
    "2728": "Politeknik Negeri Nusa Utara",
    "2831": "Politeknik Negeri Ambon",
    "2832": "Politeknik Perikanan Negeri Tual",
    "2931": "Politeknik Negeri Fakfak",
}

# ===================================================================
# JENJANG NORMALIZATION: SNBT -> BAN-PT
# ===================================================================
JENJANG_MAP = {
    "sarjana": "S1",
    "sarjana terapan": "D4",
    "magister": "S2",
    "doktor": "S3",
    "profesi": "Profesi",
    "spesialis": "Spesialis",
    "subspesialis": "Subspesialis",
    "d-iii": "D-III",
    "d-iv": "D-IV",
    "d3": "D-III",
    "d4": "D-IV",
    # BAN-PT raw values
    "s1": "S1",
    "s2": "S2",
    "s3": "S3",
    "d-i": "D-I",
    "d-ii": "D-II",
    "d-iii": "D-III",
    "d-iv": "D-IV",
    "sarjana terapan": "D4",
    "magister terapan": "S2 Terapan",
    "doktor terapan": "S3 Terapan",
    "diploma tiga": "D-III",
    "diploma empat": "D-IV",
    "diploma ii": "D-II",
    "diploma i": "D-I",
    "diploma 3": "D-III",
    "diploma 4": "D-IV",
}

def norm_jen(j):
    if not j:
        return j
    j_clean = j.strip().lower()
    return JENJANG_MAP.get(j_clean, j.strip().upper())


def clean(s):
    """Normalize prodi name for matching."""
    s = s.upper().strip()
    s = re.sub(r'[,.\-&/()]+', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s


def inst_base_name(s):
    """Strip location suffix (', CITY') from institution name."""
    s = s.upper().strip()
    # Remove ", CITY" suffix
    if ',' in s:
        s = s.split(',')[0].strip()
    return s


def build_akred_index(akred_records):
    """Build index: (institusi_base, jenjang_norm) -> list of akred records."""
    index = defaultdict(list)
    for r in akred_records:
        inst = inst_base_name(r[0])
        jen = norm_jen(r[2])
        p_clean = clean(r[1])
        index[(inst, jen)].append({
            "prodi_raw": r[1],
            "prodi_clean": p_clean,
            "jenjang_raw": r[2],
            "jenjang_norm": jen,
            "no_sk": r[4],
            "tahun": r[5],
            "nilai": r[6],
            "tgl_expired": r[7],
            "status": r[8],
        })
    return index


def find_akred(snbt_prodi_name, snbt_jenjang, akred_records):
    """
    Find best akred match for a SNBT prodi.
    Returns (match_method, akred_record) or None.
    Methods: 'exact', 'jenjang_fallback', 'fuzzy', None
    """
    snbt_clean = clean(snbt_prodi_name)
    snbt_jen = norm_jen(snbt_jenjang)
    snbt_words = set(snbt_clean.split())

    # Group by jenjang
    by_jen = defaultdict(list)
    for ak in akred_records:
        by_jen[ak['jenjang_norm']].append(ak)

    # Strategy 1: exact match on clean name + jenjang
    if snbt_jen in by_jen:
        for ak in by_jen[snbt_jen]:
            if snbt_clean == ak['prodi_clean']:
                return ('exact', ak)

    # Strategy 2: exact match on clean name, any jenjang S1/D4 overlap
    for jen, recs in by_jen.items():
        if jen == snbt_jen:
            continue
        # Allow S1<->Sarjana, D4<->Sarjana Terapan as same
        same_group = (
            (snbt_jen in ('S1', 'Sarjana') and jen in ('S1', 'Sarjana')) or
            (snbt_jen in ('D4', 'Sarjana Terapan') and jen in ('D4', 'Sarjana Terapan'))
        )
        if same_group:
            for ak in recs:
                if snbt_clean == ak['prodi_clean']:
                    return ('jenjang_fallback', ak)

    # Strategy 3: partial substring match
    if snbt_jen in by_jen:
        for ak in by_jen[snbt_jen]:
            if snbt_clean in ak['prodi_clean'] or ak['prodi_clean'] in snbt_clean:
                return ('partial', ak)

    # Strategy 4: word overlap (at least 2 significant words)
    if snbt_jen in by_jen:
        best_score = 0
        best_ak = None
        for ak in by_jen[snbt_jen]:
            ak_words = set(ak['prodi_clean'].split())
            # Filter stopwords
            stopwords = {'dan', 'di', 'ke', 'dan', 'atau', 'serta', 'untuk', 'ilmu', 'stud'}
            significant_snbt = snbt_words - stopwords
            significant_ak = ak_words - stopwords
            if not significant_snbt or not significant_ak:
                continue
            common = significant_snbt & significant_ak
            if len(common) >= 2:
                score = len(common) / max(len(significant_snbt), len(significant_ak))
                if score >= 0.5 and score > best_score:
                    best_score = score
                    best_ak = ak
        if best_ak:
            return ('fuzzy', best_ak)

    return None


def merge_ptn(kode, akred_index):
    """Merge akreditasi into SNBT prodi data for one PTN."""
    snbt_path = os.path.join(DATA_DIR, f"{kode}.json")
    if not os.path.exists(snbt_path):
        return None

    with open(snbt_path, 'r') as f:
        ptn_data = json.load(f)

    inst_name = NAME_MAP.get(kode)
    if not inst_name:
        return None

    inst_upper = inst_name.upper()
    jenjangs = set(ak[1] for ak in akred_index.keys() if ak[0] == inst_upper)

    if not jenjangs:
        return None

    # Collect all akred records for this institution
    all_akred = []
    for j in jenjangs:
        all_akred.extend(akred_index[(inst_upper, j)])

    merged = []
    matched_count = 0
    for prodi in ptn_data['data']:
        ak = find_akred(prodi['nama'], prodi['jenjang'], all_akred)
        if ak:
            matched_count += 1
            method, akred_rec = ak
            merged_prodi = {
                **prodi,
                "akreditasi": {
                    "nilai": akred_rec['nilai'],
                    "no_sk": akred_rec['no_sk'],
                    "tahun": akred_rec['tahun'],
                    "tgl_expired": akred_rec['tgl_expired'],
                    "status": akred_rec['status'],
                    "jenjang_akred": akred_rec['jenjang_raw'],
                    "match_method": method,
                }
            }
        else:
            merged_prodi = {
                **prodi,
                "akreditasi": None,
            }
        merged.append(merged_prodi)

    return {
        "kode": kode,
        "nama": inst_name,
        "prodi_count": ptn_data.get('prodi_count'),
        "web": ptn_data.get('web'),
        "match_stats": {
            "total": len(ptn_data['data']),
            "matched": matched_count,
            "unmatched": len(ptn_data['data']) - matched_count,
        },
        "data": merged,
    }


def main():
    print("Loading akreditasi.json...")
    with open(AKRED_PATH, 'r') as f:
        akred_all = json.load(f)['data']

    print(f"Total akreditasi records: {len(akred_all)}")
    print("Building index...")
    akred_index = build_akred_index(akred_all)

    # Get list of PTN files
    ptn_files = glob.glob(os.path.join(DATA_DIR, "*.json"))
    # Exclude merged files
    ptn_files = [f for f in ptn_files if '_akreditasi' not in f and 'unis' not in f]
    ptn_kodes = sorted(set(os.path.basename(f).replace('.json', '') for f in ptn_files))

    print(f"Found {len(ptn_kodes)} PTN data files")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    stats = {"ok": 0, "fail": 0, "total_matched": 0, "total_prodi": 0}
    results = []

    for kode in ptn_kodes:
        result = merge_ptn(kode, akred_index)
        if result:
            out_path = os.path.join(OUTPUT_DIR, f"{kode}_akreditasi.json")
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, separators=(',', ':'))
            s = result['match_stats']
            pct = s['matched'] / s['total'] * 100 if s['total'] > 0 else 0
            print(f"  {kode} {result['nama'][:40]}: {s['matched']}/{s['total']} matched ({pct:.0f}%)")
            stats['ok'] += 1
            stats['total_matched'] += s['matched']
            stats['total_prodi'] += s['total']
            results.append(result)
        else:
            print(f"  {kode}: FAILED (no data or no mapping)")
            stats['fail'] += 1

    print(f"\nDone: {stats['ok']} PTN OK, {stats['fail']} failed")
    print(f"Total: {stats['total_matched']}/{stats['total_prodi']} prodi matched ({stats['total_matched']/stats['total_prodi']*100:.1f}%)")
    print(f"Output: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
