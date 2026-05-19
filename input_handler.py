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
    """Konversi nilai apapun ke float, kembalikan 0.0 jika gagal."""
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
# MAPPING: label di template → field di dataclass
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
    "Free Cash Flow":           None,  # dihitung via @property, dilewati
}

LABEL_PASAR = {
    "Harga Saham":              "harga_saham",
    "Market Cap":               "market_cap",
    "Enterprise Value":         "enterprise_value",
}


# ══════════════════════════════════════════════════════
# BACA SHEET
# ══════════════════════════════════════════════════════

def _baca_sheet(xls: pd.ExcelFile, nama_sheet: str,
                label_map: dict) -> dict[int, dict]:
    """
    Baca satu sheet template dan kembalikan dict:
        { tahun: { field_name: nilai, ... }, ... }

    Struktur sheet template:
        baris 0  : judul       → dilewati
        baris 1  : header      → kolom ke-4 dst berisi tahun
        baris 2+ : data item   → kolom 1 berisi label
    """
    df = pd.read_excel(xls, sheet_name=nama_sheet, header=None)

    # cari kolom tahun dari baris header (baris index 1)
    tahun_cols = {}   # { index_kolom: tahun }
    for col_idx, val in enumerate(df.iloc[1]):
        try:
            v = int(_safe_float(val))
            if 2000 <= v <= 2099:
                tahun_cols[col_idx] = v
        except (ValueError, TypeError):
            pass

    if not tahun_cols:
        print(f"  [PERINGATAN] Sheet '{nama_sheet}': kolom tahun tidak ditemukan.")
        return {}

    # siapkan wadah hasil per tahun
    hasil = {t: {"tahun": t} for t in tahun_cols.values()}

    # baca baris data satu per satu
    for row_idx in range(2, len(df)):
        row = df.iloc[row_idx]

        # kolom 1 = label item laporan keuangan
        label_raw = str(row.iloc[1]).strip()

        # lewati baris kosong dan section header (▌ ...)
        if not label_raw or label_raw in ("nan", "None"):
            continue
        if label_raw.startswith("▌"):
            continue

        # bersihkan prefix "* " (wajib) dan "  " (opsional)
        label = label_raw.replace("* ", "").replace("  ", "").strip()

        # cari field yang sesuai di mapping
        if label not in label_map:
            continue

        field_name = label_map[label]

        # None berarti kolom kalkulasi (Free Cash Flow) — lewati
        if field_name is None:
            continue

        # ambil nilai dari setiap kolom tahun
        for col_idx, tahun in tahun_cols.items():
            nilai = _safe_float(row.iloc[col_idx] if col_idx < len(row) else None)
            hasil[tahun][field_name] = nilai

    return hasil


def _baca_profil(xls: pd.ExcelFile) -> Optional[CompanyProfile]:
    """
    Baca sheet Profil dari template.
    Kolom A = label, kolom B = nilai yang diisi pengguna.
    """
    df = pd.read_excel(xls, sheet_name="Profil", header=None)
    df = df.dropna(how="all")

    # bangun dict label → nilai dari kolom A dan B
    peta = {}
    for _, row in df.iterrows():
        if len(row) >= 2 and pd.notna(row.iloc[0]):
            label = str(row.iloc[0]).strip().replace("* ", "").replace("  ", "")
            nilai = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            peta[label] = nilai

    nama   = peta.get("Nama Perusahaan", "").strip()
    ticker = peta.get("Ticker", "").strip()
    sektor = peta.get("Sektor", "Lainnya").strip()
    sub    = peta.get("Sub Sektor", "").strip()
    harga  = _safe_float(peta.get("Harga Pasar", 0))

    if not nama or not ticker:
        return None

    return CompanyProfile(
        nama=nama,
        ticker=ticker,
        sektor=sektor,
        sub_sektor=sub,
        harga_pasar=harga,
    )


def _dict_ke_dataclass(data_dict: dict, Kelas):
    """
    Konversi dict hasil _baca_sheet ke objek dataclass.
    Hanya field yang ada di dataclass yang diteruskan.
    """
    fields_valid = Kelas.__dataclass_fields__.keys()
    kw = {k: v for k, v in data_dict.items() if k in fields_valid}
    return Kelas(**kw)


# ══════════════════════════════════════════════════════
# KELAS UTAMA
# ══════════════════════════════════════════════════════

class InputHandler:
    """
    Membaca file Excel template FinSight dan mengembalikan CompanyData.

    Contoh:
        handler = InputHandler()
        data    = handler.dari_excel("data/tlkm.xlsx")
    """

    def dari_excel(self, path: str | Path) -> Optional[CompanyData]:
        """
        Baca file template_input.xlsx yang sudah diisi pengguna.

        Parameter:
            path : lokasi file .xlsx

        Return:
            CompanyData jika berhasil, None jika gagal
        """
        path = Path(path)

        # validasi file
        if not path.exists():
            print(f"\n  ERROR: File tidak ditemukan: {path}")
            print(f"  Template tersedia di: {cfg.TEMPLATES_DIR / 'template_input.xlsx'}")
            return None

        if path.suffix.lower() not in (".xlsx", ".xlsm"):
            print(f"  ERROR: Format tidak didukung ({path.suffix}). Gunakan .xlsx")
            return None

        print(f"\n  Membaca: {path.name}")

        try:
            xls = pd.ExcelFile(path)

            # baca profil
            profil = _baca_profil(xls)
            if profil is None:
                print("  ERROR: Sheet 'Profil' tidak lengkap.")
                print("  Pastikan Nama Perusahaan dan Ticker sudah diisi.")
                return None

            # baca empat sheet laporan keuangan
            data_neraca = _baca_sheet(xls, "Neraca",    LABEL_NERACA)
            data_lr     = _baca_sheet(xls, "LabaRugi",  LABEL_LABA_RUGI)
            data_cf     = _baca_sheet(xls, "ArusKas",   LABEL_ARUS_KAS)
            data_pasar  = _baca_sheet(xls, "DataPasar", LABEL_PASAR)

            # konversi dict → dataclass
            neraca_list = [_dict_ke_dataclass(d, BalanceSheet)    for d in data_neraca.values()]
            lr_list     = [_dict_ke_dataclass(d, IncomeStatement)  for d in data_lr.values()]
            cf_list     = [_dict_ke_dataclass(d, CashFlow)         for d in data_cf.values()]
            mp_list     = [_dict_ke_dataclass(d, MarketData)       for d in data_pasar.values()]

            # pakai harga saham terbaru dari DataPasar jika profil kosong
            if profil.harga_pasar <= 0 and mp_list:
                profil.harga_pasar = mp_list[-1].harga_saham

            # rakit CompanyData
            data = CompanyData(
                profil=profil,
                neraca=neraca_list,
                laba_rugi=lr_list,
                arus_kas=cf_list,
                data_pasar=mp_list,
            )

            self._tampilkan_ringkasan(data)
            return data

        except Exception as e:
            print(f"  ERROR: Gagal membaca file — {e}")
            return None

    def _tampilkan_ringkasan(self, data: CompanyData) -> None:
        """Cetak ringkasan data yang berhasil dimuat."""
        valid, errors = data.validasi()

        print()
        print("  " + "=" * 48)
        print(f"  {data.profil.nama} ({data.profil.ticker})")
        print(f"  Sektor  : {data.profil.sektor}")
        print(f"  Periode : {', '.join(map(str, data.tahun_tersedia))} ({data.jumlah_tahun} tahun)")
        print(f"  Harga   : Rp {data.profil.harga_pasar:,.0f}")
        print("  " + "-" * 48)

        laporan = [
            ("Neraca",     data.neraca),
            ("Laba Rugi",  data.laba_rugi),
            ("Arus Kas",   data.arus_kas),
            ("Data Pasar", data.data_pasar),
        ]
        for nama, items in laporan:
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