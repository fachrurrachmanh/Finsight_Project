"""
modules/input_handler.py
=========================
Membaca file template_input.xlsx dan mengembalikan CompanyData.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
from typing import Optional

import config as cfg
from models.company import CompanyProfile, CompanyData
from models.financial_data import BalanceSheet, IncomeStatement, CashFlow, MarketData


# ══════════════════════════════════════════════════════
# HELPER
# ══════════════════════════════════════════════════════

def _safe_float(val) -> float:
    if val is None:
        return 0.0
    try:
        s = str(val).strip().replace(",", "")
        if s in ("", "-", "nan", "NaN", "N/A", "None"):
            return 0.0
        return float(s)
    except (ValueError, TypeError):
        return 0.0


# ══════════════════════════════════════════════════════
# MAPPING: label template → field class
# None = kolom kalkulasi, dilewati
# ══════════════════════════════════════════════════════

LABEL_NERACA = {
    "Kas & Setara Kas":         "kas_setara_kas",
    "Piutang Usaha":            "piutang_usaha",
    "Persediaan":               "persediaan",
    "Aset Lancar Lain":         "aset_lancar_lain",
    "Total Aset Lancar":        "total_aset_lancar",
    "Aset Tetap (Neto)":        "aset_tetap_neto",
    "Goodwill":                 "goodwill",
    "Aset Tidak Berwujud":      "aset_tidak_berwujud",
    "Aset Tidak Lancar Lain":   "aset_tidak_lancar_lain",
    "Total Aset Tidak Lancar":  "total_aset_tidak_lancar",
    "Total Aset":               "total_aset",
    "Utang Usaha":              "utang_usaha",
    "Utang Jangka Pendek":      "utang_jangka_pendek",
    "Liabilitas Lancar Lain":   "liabilitas_lancar_lain",
    "Total Liabilitas Lancar":  "total_liabilitas_lancar",
    "Utang Jangka Panjang":     "utang_jangka_panjang",
    "Liabilitas Tidak Lancar":  "liabilitas_tidak_lancar_lain",
    "Total Liabilitas":         "total_liabilitas",
    "Modal Disetor":            "modal_disetor",
    "Laba Ditahan":             "laba_ditahan",
    "Ekuitas Lain":             "ekuitas_lain",
    "Total Ekuitas":            "total_ekuitas",
    "Jumlah Saham Beredar":     "jumlah_saham_beredar",
}

LABEL_LABA_RUGI = {
    "Pendapatan":               "pendapatan",
    "HPP":                      "harga_pokok_penjualan",
    "Laba Kotor":               "laba_kotor",
    "Beban Operasional":        "beban_operasional",
    "Depresiasi & Amortisasi":  "beban_penyusutan",
    "EBIT":                     "ebit",
    "EBITDA":                   "ebitda",
    "Beban Bunga":              "beban_bunga",
    "Pendapatan/Beban Lain":    "pendapatan_lain",
    "Laba Sebelum Pajak":       "laba_sebelum_pajak",
    "Pajak":                    "pajak",
    "Laba Bersih":              "laba_bersih",
    "EPS":                      "eps",
    "DPS":                      "dps",
    "Jumlah Saham Beredar":     "jumlah_saham_beredar",
}

LABEL_ARUS_KAS = {
    "Arus Kas dari Operasi":    "arus_kas_operasi",
    "Depresiasi & Amortisasi":  "depresiasi_amortisasi",
    "Perubahan Modal Kerja":    "perubahan_modal_kerja",
    "Capex":                    "capex",
    "Akuisisi":                 "akuisisi",
    "Arus Kas Investasi":       "arus_kas_investasi",
    "Penerbitan Utang":         "penerbitan_utang",
    "Pembayaran Utang":         "pembayaran_utang",
    "Penerbitan Saham":         "penerbitan_saham",
    "Dividen Dibayar":          "dividen_dibayar",
    "Buyback Saham":            "buyback_saham",
    "Arus Kas Pendanaan":       "arus_kas_pendanaan",
    "Perubahan Kas Bersih":     "perubahan_kas",
    "Free Cash Flow":           None,
}

LABEL_PASAR = {
    "Harga Saham":              "harga_saham",
    "Market Cap":               "market_cap",
    "Enterprise Value":         "enterprise_value",
}


# ══════════════════════════════════════════════════════
# BACA SHEET
# ══════════════════════════════════════════════════════

def _baca_sheet(xls, nama_sheet, label_map):
    """
    Baca satu sheet dan kembalikan:
        { tahun: { field: nilai, ... }, ... }

    Struktur template:
        baris 0  : judul      -> dilewati
        baris 1  : header     -> kolom 4+ berisi tahun
        baris 2+ : data item  -> kolom 1 berisi label
    """
    df = pd.read_excel(xls, sheet_name=nama_sheet, header=None)

    # cari kolom tahun dari baris index 1
    tahun_cols = {}
    for col_idx, val in enumerate(df.iloc[1]):
        try:
            v = int(_safe_float(val))
            if 2000 <= v <= 2099:
                tahun_cols[col_idx] = v
        except (ValueError, TypeError):
            pass

    if not tahun_cols:
        print(f"  PERINGATAN: Sheet '{nama_sheet}' tidak memiliki kolom tahun.")
        return {}

    # wadah hasil
    hasil = {t: {"tahun": t} for t in tahun_cols.values()}

    # baca tiap baris data
    for i in range(2, len(df)):
        row = df.iloc[i]

        label_raw = str(row.iloc[1]).strip()

        # lewati baris kosong dan section header
        if not label_raw or label_raw in ("nan", "None"):
            continue
        if label_raw.startswith("▌"):
            continue

        # bersihkan prefix
        label = label_raw.replace("* ", "").replace("  ", "").strip()

        if label not in label_map or label_map[label] is None:
            continue

        field = label_map[label]

        for col_idx, tahun in tahun_cols.items():
            nilai = _safe_float(row.iloc[col_idx] if col_idx < len(row) else None)
            hasil[tahun][field] = nilai

    return hasil


def _baca_profil(xls):
    """Baca sheet Profil. Kolom A = label, kolom B = nilai."""
    df = pd.read_excel(xls, sheet_name="Profil", header=None)
    df = df.dropna(how="all")

    peta = {}
    for _, row in df.iterrows():
        if len(row) >= 2 and pd.notna(row.iloc[0]):
            label = str(row.iloc[0]).strip().replace("* ", "").replace("  ", "")
            nilai = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            peta[label] = nilai

    nama   = peta.get("Nama Perusahaan", "").strip()
    ticker = peta.get("Ticker", "").strip()

    if not nama or not ticker:
        return None

    return CompanyProfile(
        nama   = nama,
        ticker = ticker,
        sektor = peta.get("Sektor", "Lainnya").strip(),
        sub_sektor = peta.get("Sub Sektor", "").strip(),
        harga_pasar = _safe_float(peta.get("Harga Pasar", 0)),
    )


def _buat_objek(data_dict, Kelas):
    """Buat objek dari dict — hanya kirim field yang dikenal class."""
    field_valid = vars(Kelas()).keys()
    kw = {k: v for k, v in data_dict.items() if k in field_valid}
    return Kelas(**kw)


# ══════════════════════════════════════════════════════
# KELAS UTAMA
# ══════════════════════════════════════════════════════

class InputHandler:

    def dari_excel(self, path):
        path = Path(path)

        if not path.exists():
            print(f"\n  ERROR: File tidak ditemukan — {path}")
            print(f"  Template: {cfg.TEMPLATES_DIR / 'template_input.xlsx'}")
            return None

        if path.suffix.lower() not in (".xlsx", ".xlsm"):
            print(f"  ERROR: Gunakan file .xlsx dari template FinSight.")
            return None

        print(f"\n  Membaca: {path.name}")

        try:
            xls = pd.ExcelFile(path)

            profil = _baca_profil(xls)
            if profil is None:
                print("  ERROR: Sheet Profil tidak lengkap (Nama & Ticker wajib diisi).")
                return None

            data_neraca = _baca_sheet(xls, "Neraca",    LABEL_NERACA)
            data_lr     = _baca_sheet(xls, "LabaRugi",  LABEL_LABA_RUGI)
            data_cf     = _baca_sheet(xls, "ArusKas",   LABEL_ARUS_KAS)
            data_pasar  = _baca_sheet(xls, "DataPasar", LABEL_PASAR)

            neraca_list = [_buat_objek(d, BalanceSheet)    for d in data_neraca.values()]
            lr_list     = [_buat_objek(d, IncomeStatement)  for d in data_lr.values()]
            cf_list     = [_buat_objek(d, CashFlow)         for d in data_cf.values()]
            mp_list     = [_buat_objek(d, MarketData)       for d in data_pasar.values()]

            if profil.harga_pasar <= 0 and mp_list:
                profil.harga_pasar = mp_list[-1].harga_saham

            data = CompanyData(
                profil    = profil,
                neraca    = neraca_list,
                laba_rugi = lr_list,
                arus_kas  = cf_list,
                data_pasar = mp_list,
            )

            self._ringkasan(data)
            return data

        except Exception as e:
            print(f"  ERROR: {e}")
            return None

    def _ringkasan(self, data):
        valid, errors = data.validasi()
        print()
        print("  " + "=" * 48)
        print(f"  {data.profil.nama} ({data.profil.ticker})")
        print(f"  Sektor  : {data.profil.sektor}")
        print(f"  Periode : {', '.join(map(str, data.tahun_tersedia()))} ({data.jumlah_tahun()} tahun)")
        print(f"  Harga   : Rp {data.profil.harga_pasar:,.0f}")
        print("  " + "-" * 48)
        for nama, items in [("Neraca", data.neraca), ("Laba Rugi", data.laba_rugi),
                             ("Arus Kas", data.arus_kas), ("Data Pasar", data.data_pasar)]:
            status = "OK" if len(items) >= cfg.GRAHAM["min_years_data"] else "KURANG"
            tahun  = ", ".join(str(x.tahun) for x in items) if items else "-"
            print(f"  {nama:<12}: {tahun}  [{status}]")
        print("  " + "-" * 48)
        if errors:
            for e in errors:
                print(f"  PERINGATAN: {e}")
        else:
            print("  Data siap dianalisis.")
        print("  " + "=" * 48)
        print()