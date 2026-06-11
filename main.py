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
from sort_utils import merge_sort


# ══════════════════════════════════════════════════════
# HELPER TAMPILAN
# ══════════════════════════════════════════════════════

def garis(kar="=", lebar=60):
    return kar * lebar

def print_header():
    os.system("cls" if os.name == "nt" else "clear")
    print(garis())
    print("  FinSight CLI  v" + cfg.APP_VERSION)
    print("  " + cfg.APP_DESCRIPTION)
    print(garis())
    print()

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
        path_str = tanya("Path file Excel (.xlsx)")
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
    print()
    print(garis())
    print("  MEMULAI ANALISIS")
    print(garis())

    # ── langkah 1: baca Excel ─────────────────────────
    print("\n  [1/5] Membaca data dari Excel...")
    handler = InputHandler()
    data    = handler.dari_excel(path_excel)

    if data is None:
        print("\n  ERROR: Gagal membaca file Excel.")
        print("  Pastikan file menggunakan template FinSight.")
        return None

    valid, errors = data.validasi()
    if not valid:
        print("\n  PERINGATAN: Data tidak lengkap:")
        for e in errors:
            print(f"    - {e}")
        lanjut = input("\n  Lanjutkan analisis? (y/n): ").strip().lower()
        if lanjut != "y":
            return None

    # ── langkah 2: hitung rasio ───────────────────────
    print("\n  [2/5] Menghitung rasio keuangan...")
    ratio = RatioEngine(data)
    ratio.hitung_semua()

    # ── langkah 3: analisis Graham ────────────────────
    print("\n  [3/5] Menjalankan analisis Graham...")

    # tanya parameter DCF
    print()
    print("  Parameter analisis (Enter = gunakan default):")
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
    print("\n  [4/5] Menjalankan analisis risiko...")
    risk = RiskAnalyzer(data)
    risk.analisis()

    # ── langkah 5: buat laporan ───────────────────────
    print("\n  [5/5] Menyusun laporan...")
    reporter = Reporter(data, ratio, graham, risk)
    reporter.buat_laporan()

    return reporter


def pilih_output(reporter):
    """
    Tanya pengguna format output dan bagian yang ingin ditampilkan.
    """
    print()
    print(garis())
    print("  OUTPUT LAPORAN")
    print(garis())
    print()
    print("  Tampilkan di terminal:")
    print("  [1] Ringkasan eksekutif saja")
    print("  [2] Laporan lengkap")
    print("  [3] Lewati (langsung ke simpan file)")
    print()

    pilihan = tanya_pilihan("Pilihan tampilan", ["1", "2", "3"], "1")

    if pilihan == "1":
        print()
        reporter.tampilkan_ringkasan()
    elif pilihan == "2":
        print()
        reporter.tampilkan()

    # simpan file
    print()
    print("  Simpan laporan ke file:")
    print("  [1] TXT saja")
    print("  [2] JSON saja")
    print("  [3] TXT dan JSON")
    print("  [4] Tidak simpan")
    print()

    simpan = tanya_pilihan("Pilihan simpan", ["1", "2", "3", "4"], "3")

    paths = []
    if simpan in ("1", "3"):
        p = reporter.simpan("txt")
        paths.append(p)
    if simpan in ("2", "3"):
        p = reporter.simpan("json")
        paths.append(p)

    if paths:
        print()
        print("  File tersimpan di:")
        for p in paths:
            print(f"    {p}")

    return paths


# ══════════════════════════════════════════════════════
# MENU RIWAYAT
# ══════════════════════════════════════════════════════

def tampilkan_riwayat():
    """Tampilkan daftar file laporan yang sudah tersimpan."""
    print()
    print(garis())
    print("  RIWAYAT LAPORAN TERSIMPAN")
    print(garis())
    print()

    # cari semua file laporan di outputs/
    files_txt  = merge_sort(cfg.OUTPUTS_DIR.glob("*_laporan_*.txt"),  key=lambda x: x.stat().st_mtime, reverse=True)
    files_json = merge_sort(cfg.OUTPUTS_DIR.glob("*_laporan_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    semua      = merge_sort(set(files_txt) | set(files_json),
                            key=lambda x: x.stat().st_mtime, reverse=True)

    if not semua:
        print("  Belum ada laporan tersimpan.")
        print()
        return

    for i, f in enumerate(semua[:20], 1):
        ukuran = f.stat().st_size // 1024
        print(f"  [{i:2}] {f.name:<45} {ukuran:>4} KB")

    print()
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
        print("  Nomor tidak valid.")


def _tampilkan_ringkasan_json(path):
    """Tampilkan ringkasan dari file JSON laporan."""
    import json
    try:
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        print()
        print(garis())
        meta = d.get("metadata", {})
        print(f"  {meta.get('nama','')} ({meta.get('ticker','')})")
        print(f"  Tanggal  : {meta.get('tanggal','')}")
        print(f"  Grade    : {d.get('grade','')} — {d.get('label','')}")
        print(f"  Skor     : {d.get('total_skor',0)}/100")
        val = d.get("valuasi", {})
        print(f"  MoS      : {val.get('margin_of_safety_final',0)*100:.1f}%")
        print(f"  Rekomendasi: {val.get('rekomendasi_mos','')}")
        risk = d.get("risk_dashboard", {}).get("total", {})
        print(f"  Risk     : {risk.get('skor_risiko',0)}/100 [{risk.get('level','')}]")
        flags = d.get("red_flags", [])
        print(f"  Red Flags: {len(flags)}")
        print(garis())
    except Exception as e:
        print(f"  ERROR membaca file: {e}")


def _tampilkan_txt(path):
    """Tampilkan isi file TXT laporan (100 baris pertama)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            baris = f.readlines()
        print()
        for b in baris[:100]:
            print(b, end="")
        if len(baris) > 100:
            print(f"\n  ... ({len(baris)-100} baris selanjutnya tidak ditampilkan)")
    except Exception as e:
        print(f"  ERROR membaca file: {e}")


# ══════════════════════════════════════════════════════
# INFO APLIKASI
# ══════════════════════════════════════════════════════

def tampilkan_info():
    """Tampilkan informasi aplikasi dan konfigurasi aktif."""
    print()
    print(garis())
    print("  INFORMASI APLIKASI")
    print(garis())
    print()
    print(f"  Nama       : {cfg.APP_NAME}")
    print(f"  Versi      : {cfg.APP_VERSION}")
    print(f"  Deskripsi  : {cfg.APP_DESCRIPTION}")
    print()
    print("  DIREKTORI")
    print(garis("-"))
    print(f"  Template   : {cfg.TEMPLATES_DIR}")
    print(f"  Output     : {cfg.OUTPUTS_DIR}")
    print(f"  Database   : {cfg.DB_PATH}")
    print()
    print("  THRESHOLD BENJAMIN GRAHAM")
    print(garis("-"))
    print(f"  Min MoS    : {cfg.GRAHAM['min_margin_of_safety']*100:.0f}%")
    print(f"  Max P/E    : {cfg.GRAHAM['max_pe_ratio']}x")
    print(f"  Max P/BV   : {cfg.GRAHAM['max_pb_ratio']}x")
    print(f"  Min CR     : {cfg.GRAHAM['min_current_ratio']}x")
    print(f"  Max DER    : {cfg.GRAHAM['max_der']}x")
    print(f"  Min Dividen: {cfg.GRAHAM['min_dividend_years']} tahun")
    print()
    print("  THRESHOLD RISIKO")
    print(garis("-"))
    print(f"  Altman Z aman    : > {cfg.RISK['altman_safe']}")
    print(f"  Beneish M manipulasi: > {cfg.RISK['beneish_threshold']}")
    print(f"  Springate S bangkrut: < {cfg.RISK['springate_threshold']}")
    print()
    print("  BOBOT GRAHAM SCORECARD")
    print(garis("-"))
    for k, v in cfg.SCORECARD_WEIGHTS.items():
        print(f"  {k:<30}: {v*100:.0f}%")
    print()
    print("  INPUT")
    print(garis("-"))
    print("  Hanya menerima file Excel (.xlsx)")
    print(f"  Template  : {cfg.TEMPLATES_DIR / 'template_input.xlsx'}")
    print()


# ══════════════════════════════════════════════════════
# MENU UTAMA
# ══════════════════════════════════════════════════════

def menu_utama():
    print_header()
    print("  MENU UTAMA")
    print(garis("-"))
    print("  [1] Analisis perusahaan baru")
    print("  [2] Lihat riwayat laporan")
    print("  [3] Informasi aplikasi")
    print("  [4] Keluar")
    print()
    return tanya_pilihan("Pilih menu", ["1", "2", "3", "4"], "1")


# ══════════════════════════════════════════════════════
# MAIN LOOP
# ══════════════════════════════════════════════════════

def main():
    while True:
        pilihan = menu_utama()

        if pilihan == "1":
            # ── analisis perusahaan baru ───────────────
            print_header()
            print("  ANALISIS PERUSAHAAN BARU")
            print(garis("-"))
            print()
            print(f"  Siapkan file Excel dari template:")
            print(f"  {cfg.TEMPLATES_DIR / 'template_input.xlsx'}")
            print()

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
            print_header()
            tampilkan_riwayat()
            input("  Tekan Enter untuk kembali ke menu...")

        elif pilihan == "3":
            # ── info aplikasi ──────────────────────────
            print_header()
            tampilkan_info()
            input("  Tekan Enter untuk kembali ke menu...")

        elif pilihan == "4":
            print()
            print("  Terima kasih telah menggunakan FinSight CLI.")
            print()
            break


# ══════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Program dihentikan.")
        sys.exit(0)
        