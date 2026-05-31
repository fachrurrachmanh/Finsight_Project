"""
main.py — Entry Point FinSight CLI
====================================
Menyatukan semua modul:
  input_handler   → baca Excel
  ratio_engine    → hitung rasio keuangan
  graham_analyzer → analisis value investing Graham
  risk_analyzer   → analisis risiko keuangan
  reporter        → susun dan simpan laporan

Cara menjalankan:
  python main.py
"""

import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config as cfg
from modules.input_handler   import InputHandler
from modules.ratio_engine    import RatioEngine
from modules.graham_analyzer import GrahamAnalyzer
from modules.risk_analyzer   import RiskAnalyzer
from modules.reporter        import Reporter


# ══════════════════════════════════════════════════════
# HELPER TAMPILAN
# ══════════════════════════════════════════════════════

def garis(kar="=", lebar=60):
    return kar * lebar

def cetak(teks=""):
    print(teks)

def cetak_header():
    os.system("cls" if os.name == "nt" else "clear")
    cetak(garis())
    cetak("  FinSight CLI  v" + cfg.APP_VERSION)
    cetak("  " + cfg.APP_DESCRIPTION)
    cetak(garis())
    cetak()

def tanya(label, default=""):
    """Input teks sederhana dengan nilai default."""
    raw = input(f"  {label}" + (f" [{default}]" if default else "") + ": ").strip()
    return raw if raw else default

def tanya_pilihan(label, pilihan_valid, default=""):
    """Input dengan validasi pilihan."""
    while True:
        raw = tanya(label, default).upper()
        if raw in [p.upper() for p in pilihan_valid]:
            return raw
        print(f"  Pilihan tidak valid. Masukkan salah satu dari: {pilihan_valid}")

def tanya_path():
    """Input path file Excel dengan validasi ekstensi."""
    while True:
        path_str = tanya("Path file Excel yang ingin dianalisis (.xlsx)")
        if not path_str:
            print("  Path tidak boleh kosong.")
            continue
        path = Path(path_str)
        if not path.exists():
            print(f"  File tidak ditemukan: {path}")
            print(f"  Template tersedia di: {cfg.TEMPLATES_DIR / 'template_input.xlsx'}")
            ulang = input("  Coba lagi? (y/n): ").strip().lower()
            if ulang != "y":
                return None
            continue
        if path.suffix.lower() not in (".xlsx", ".xlsm"):
            print(f"  Format tidak didukung ({path.suffix}). Gunakan .xlsx")
            continue
        return path


# ══════════════════════════════════════════════════════
# ALUR ANALISIS UTAMA
# ══════════════════════════════════════════════════════

def jalankan_analisis(path_excel):
    """
    Alur lengkap:
      1. Baca Excel
      2. Hitung rasio
      3. Analisis Graham
      4. Analisis risiko
      5. Buat laporan
      6. Simpan output
    """
    cetak()
    cetak(garis())
    cetak("  MEMULAI ANALISIS")
    cetak(garis())

    # ── langkah 1: baca Excel ─────────────────────────
    cetak("\n  [1/5] Membaca data dari Excel...")
    handler = InputHandler()
    data    = handler.dari_excel(path_excel)

    if data is None:
        cetak("\n  ERROR: Gagal membaca file Excel.")
        cetak("  Pastikan file menggunakan template FinSight.")
        return None

    valid, errors = data.validasi()
    if not valid:
        cetak("\n  PERINGATAN: Data tidak lengkap:")
        for e in errors:
            cetak(f"    - {e}")
        lanjut = input("\n  Lanjutkan analisis? (y/n): ").strip().lower()
        if lanjut != "y":
            return None

    # ── langkah 2: hitung rasio ───────────────────────
    cetak("\n  [2/5] Menghitung rasio keuangan...")
    ratio = RatioEngine(data)
    ratio.hitung_semua()

    # ── langkah 3: analisis Graham ────────────────────
    cetak("\n  [3/5] Menjalankan analisis Graham...")

    # tanya parameter DCF
    cetak()
    cetak("  Parameter analisis (Enter = gunakan default):")
    wacc_str   = tanya("WACC / discount rate (contoh: 0.10)", "0.10")
    growth_str = tanya("Growth rate FCF (contoh: 0.05)", "0.05")
    try:
        wacc   = float(wacc_str)
        growth = float(growth_str)
    except ValueError:
        wacc   = 0.10
        growth = 0.05

    graham = GrahamAnalyzer(data, wacc=wacc, growth_rate=growth)
    graham.analisis()

    # ── langkah 4: analisis risiko ────────────────────
    cetak("\n  [4/5] Menjalankan analisis risiko...")
    risk = RiskAnalyzer(data)
    risk.analisis()

    # ── langkah 5: buat laporan ───────────────────────
    cetak("\n  [5/5] Menyusun laporan...")
    reporter = Reporter(data, ratio, graham, risk)
    reporter.buat_laporan()

    return reporter


def pilih_output(reporter):
    """
    Tanya pengguna format output dan bagian yang ingin ditampilkan.
    """
    cetak()
    cetak(garis())
    cetak("  OUTPUT LAPORAN")
    cetak(garis())
    cetak()
    cetak("  Tampilkan di terminal:")
    cetak("  [1] Ringkasan eksekutif saja")
    cetak("  [2] Laporan lengkap")
    cetak("  [3] Lewati (langsung ke simpan file)")
    cetak()

    pilihan = tanya_pilihan("Pilihan tampilan", ["1", "2", "3"], "1")

    if pilihan == "1":
        cetak()
        reporter.tampilkan_ringkasan()
    elif pilihan == "2":
        cetak()
        reporter.tampilkan()

    # simpan file
    cetak()
    cetak("  Simpan laporan ke file:")
    cetak("  [1] TXT saja")
    cetak("  [2] JSON saja")
    cetak("  [3] TXT dan JSON")
    cetak("  [4] Tidak simpan")
    cetak()

    simpan = tanya_pilihan("Pilihan simpan", ["1", "2", "3", "4"], "3")

    paths = []
    if simpan in ("1", "3"):
        p = reporter.simpan("txt")
        paths.append(p)
    if simpan in ("2", "3"):
        p = reporter.simpan("json")
        paths.append(p)

    if paths:
        cetak()
        cetak("  File tersimpan di:")
        for p in paths:
            cetak(f"    {p}")

    return paths


# ══════════════════════════════════════════════════════
# MENU RIWAYAT
# ══════════════════════════════════════════════════════

def tampilkan_riwayat():
    """Tampilkan daftar file laporan yang sudah tersimpan."""
    cetak()
    cetak(garis())
    cetak("  RIWAYAT LAPORAN TERSIMPAN")
    cetak(garis())
    cetak()

    # cari semua file laporan di outputs/
    files_txt  = sorted(cfg.OUTPUTS_DIR.glob("*_laporan_*.txt"),  reverse=True)
    files_json = sorted(cfg.OUTPUTS_DIR.glob("*_laporan_*.json"), reverse=True)
    semua      = sorted(set(files_txt) | set(files_json),
                        key=lambda x: x.stat().st_mtime, reverse=True)

    if not semua:
        cetak("  Belum ada laporan tersimpan.")
        cetak()
        return

    for i, f in enumerate(semua[:20], 1):
        ukuran = f.stat().st_size // 1024
        cetak(f"  [{i:2}] {f.name:<45} {ukuran:>4} KB")

    cetak()
    buka = input("  Nomor file untuk dibuka (Enter = kembali): ").strip()
    if not buka:
        return

    try:
        idx  = int(buka) - 1
        file = semua[idx]
        if file.suffix == ".json":
            _tampilkan_ringkasan_json(file)
        else:
            _tampilkan_txt(file)
    except (ValueError, IndexError):
        cetak("  Nomor tidak valid.")


def _tampilkan_ringkasan_json(path):
    """Tampilkan ringkasan dari file JSON laporan."""
    import json
    try:
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        cetak()
        cetak(garis())
        meta = d.get("metadata", {})
        cetak(f"  {meta.get('nama','')} ({meta.get('ticker','')})")
        cetak(f"  Tanggal  : {meta.get('tanggal','')}")
        cetak(f"  Grade    : {d.get('grade','')} — {d.get('label','')}")
        cetak(f"  Skor     : {d.get('total_skor',0)}/100")
        val = d.get("valuasi", {})
        cetak(f"  MoS      : {val.get('margin_of_safety_final',0)*100:.1f}%")
        cetak(f"  Rekomendasi: {val.get('rekomendasi_mos','')}")
        risk = d.get("risk_dashboard", {}).get("total", {})
        cetak(f"  Risk     : {risk.get('skor_risiko',0)}/100 [{risk.get('level','')}]")
        flags = d.get("red_flags", [])
        cetak(f"  Red Flags: {len(flags)}")
        cetak(garis())
    except Exception as e:
        cetak(f"  ERROR membaca file: {e}")


def _tampilkan_txt(path):
    """Tampilkan isi file TXT laporan (100 baris pertama)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            baris = f.readlines()
        cetak()
        for b in baris[:100]:
            print(b, end="")
        if len(baris) > 100:
            cetak(f"\n  ... ({len(baris)-100} baris selanjutnya tidak ditampilkan)")
    except Exception as e:
        cetak(f"  ERROR membaca file: {e}")


# ══════════════════════════════════════════════════════
# INFO APLIKASI
# ══════════════════════════════════════════════════════

def tampilkan_info():
    """Tampilkan informasi aplikasi dan konfigurasi aktif."""
    cetak()
    cetak(garis())
    cetak("  INFORMASI APLIKASI")
    cetak(garis())
    cetak()
    cetak(f"  Nama       : {cfg.APP_NAME}")
    cetak(f"  Versi      : {cfg.APP_VERSION}")
    cetak(f"  Deskripsi  : {cfg.APP_DESCRIPTION}")
    cetak()
    cetak("  DIREKTORI")
    cetak(garis("-"))
    cetak(f"  Template   : {cfg.TEMPLATES_DIR}")
    cetak(f"  Output     : {cfg.OUTPUTS_DIR}")
    cetak(f"  Database   : {cfg.DB_PATH}")
    cetak()
    cetak("  THRESHOLD BENJAMIN GRAHAM")
    cetak(garis("-"))
    cetak(f"  Min MoS    : {cfg.GRAHAM['min_margin_of_safety']*100:.0f}%")
    cetak(f"  Max P/E    : {cfg.GRAHAM['max_pe_ratio']}x")
    cetak(f"  Max P/BV   : {cfg.GRAHAM['max_pb_ratio']}x")
    cetak(f"  Min CR     : {cfg.GRAHAM['min_current_ratio']}x")
    cetak(f"  Max DER    : {cfg.GRAHAM['max_der']}x")
    cetak(f"  Min Dividen: {cfg.GRAHAM['min_dividend_years']} tahun")
    cetak()
    cetak("  THRESHOLD RISIKO")
    cetak(garis("-"))
    cetak(f"  Altman Z aman    : > {cfg.RISK['altman_safe']}")
    cetak(f"  Beneish M manipulasi: > {cfg.RISK['beneish_threshold']}")
    cetak(f"  Springate S bangkrut: < {cfg.RISK['springate_threshold']}")
    cetak()
    cetak("  BOBOT GRAHAM SCORECARD")
    cetak(garis("-"))
    for k, v in cfg.SCORECARD_WEIGHTS.items():
        cetak(f"  {k:<30}: {v*100:.0f}%")
    cetak()
    cetak("  INPUT")
    cetak(garis("-"))
    cetak("  Hanya menerima file Excel (.xlsx)")
    cetak(f"  Template  : {cfg.TEMPLATES_DIR / 'template_input.xlsx'}")
    cetak()


# ══════════════════════════════════════════════════════
# MENU UTAMA
# ══════════════════════════════════════════════════════

def menu_utama():
    cetak_header()
    cetak("  MENU UTAMA")
    cetak(garis("-"))
    cetak("  [1] Analisis perusahaan baru")
    cetak("  [2] Lihat riwayat laporan")
    cetak("  [3] Informasi aplikasi")
    cetak("  [4] Keluar")
    cetak()
    return tanya_pilihan("Pilih menu", ["1", "2", "3", "4"], "1")


# ══════════════════════════════════════════════════════
# MAIN LOOP
# ══════════════════════════════════════════════════════

def main():
    while True:
        pilihan = menu_utama()

        if pilihan == "1":
            # ── analisis perusahaan baru ───────────────
            cetak_header()
            cetak("  ANALISIS PERUSAHAAN BARU")
            cetak(garis("-"))
            cetak()
            cetak(f"  Copy file template Excel, lalu isi dengan data perusahaan untuk input program")
            cetak(f"  Alamat file template: {cfg.TEMPLATES_DIR / 'template_input.xlsx'}")
            cetak()

            path = tanya_path()
            if path is None:
                continue

            reporter = jalankan_analisis(path)
            if reporter is None:
                input("\n  Tekan Enter untuk kembali ke menu...")
                continue

            pilih_output(reporter)
            input("\n  Tekan Enter untuk kembali ke menu...")

        elif pilihan == "2":
            # ── riwayat laporan ────────────────────────
            cetak_header()
            tampilkan_riwayat()
            input("  Tekan Enter untuk kembali ke menu...")

        elif pilihan == "3":
            # ── info aplikasi ──────────────────────────
            cetak_header()
            tampilkan_info()
            input("  Tekan Enter untuk kembali ke menu...")

        elif pilihan == "4":
            cetak()
            cetak("  Terima kasih telah menggunakan FinSight CLI.")
            cetak()
            break


# ══════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cetak("\n\n  Program dihentikan.")
        sys.exit(0)
