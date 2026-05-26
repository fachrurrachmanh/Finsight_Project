"""
modules/reporter.py
====================
Menyatukan hasil dari RatioEngine, GrahamAnalyzer, dan RiskAnalyzer
menjadi laporan final yang tersimpan ke file.

Format output:
  - TXT  : laporan teks lengkap di terminal dan file
  - JSON : data terstruktur untuk integrasi sistem lain

Struktur data (rubrik):
  - Single Linked List   : rantai bagian laporan
  - Double Linked List   : navigasi antar bagian laporan
  - Circular Linked List : rotasi format output
  - Stack                : riwayat laporan yang dibuat
  - Queue                : antrian bagian yang akan dicetak
  - Hash Table           : index cepat ke bagian laporan
  - Tree                 : hierarki struktur laporan
  - List/Tuple/Set/Dict  : wadah data laporan
  - Sorting              : urutkan rasio dan temuan
  - Searching            : cari bagian dan data tertentu
  - Rekursif             : cetak pohon, hitung ringkasan
  - File Handler         : tulis dan baca file laporan
  - OOP                  : class Reporter
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config as cfg
from models.company import CompanyData
from modules.ratio_engine    import RatioEngine
from modules.graham_analyzer import GrahamAnalyzer
from modules.risk_analyzer   import RiskAnalyzer


# ══════════════════════════════════════════════════════
# HELPER
# ══════════════════════════════════════════════════════

def _div(a, b, default=0.0):
    return a / b if b != 0 else default

def _garis(karakter="=", lebar=60):
    return karakter * lebar

def _fmt_rp(nilai):
    return f"Rp {nilai:>15,.0f}"

def _fmt_pct(nilai):
    return f"{nilai*100:>7.2f}%"

def _fmt_x(nilai):
    return f"{nilai:>8.2f}x"


# ══════════════════════════════════════════════════════
# SINGLE LINKED LIST — rantai bagian laporan
# ══════════════════════════════════════════════════════

class BagianNode:
    """Satu node = satu bagian laporan (misal: Profil, Rasio, Graham, dll)."""
    def __init__(self, urutan, judul, konten):
        self.urutan  = urutan   # nomor urut bagian
        self.judul   = judul    # judul bagian
        self.konten  = konten   # list of string (baris teks)
        self.next    = None


class SingleLinkedList:
    def __init__(self):
        self.head  = None
        self._ukuran = 0

    def tambah(self, urutan, judul, konten):
        node = BagianNode(urutan, judul, konten)
        if self.head is None:
            self.head = node
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = node
        self._ukuran += 1

    def cari_judul(self, judul):
        """Searching — cari bagian berdasarkan judul."""
        cur = self.head
        while cur:
            if judul.lower() in cur.judul.lower():
                return cur
            cur = cur.next
        return None

    def ke_list(self):
        hasil, cur = [], self.head
        while cur:
            hasil.append(cur)
            cur = cur.next
        return hasil

    def ukuran(self):
        return self._ukuran


# ══════════════════════════════════════════════════════
# DOUBLE LINKED LIST — navigasi antar bagian laporan
# ══════════════════════════════════════════════════════

class DoubleNode:
    def __init__(self, urutan, judul, konten):
        self.urutan = urutan
        self.judul  = judul
        self.konten = konten
        self.next   = None
        self.prev   = None


class DoubleLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def tambah(self, urutan, judul, konten):
        node = DoubleNode(urutan, judul, konten)
        if self.head is None:
            self.head = self.tail = node
            return
        node.prev      = self.tail
        self.tail.next = node
        self.tail       = node

    def bagian_pertama(self):
        return self.head

    def bagian_terakhir(self):
        return self.tail

    def maju(self, node):
        return node.next if node else None

    def mundur(self, node):
        return node.prev if node else None


# ══════════════════════════════════════════════════════
# CIRCULAR LINKED LIST — rotasi format output
# ══════════════════════════════════════════════════════

class CircularNode:
    def __init__(self, format_nama):
        self.format_nama = format_nama
        self.next        = None


class CircularLinkedList:
    def __init__(self):
        self.head    = None
        self.current = None
        self.ukuran  = 0

    def tambah(self, format_nama):
        node = CircularNode(format_nama)
        if self.head is None:
            self.head    = node
            node.next    = self.head
            self.current = self.head
        else:
            cur = self.head
            while cur.next != self.head:
                cur = cur.next
            cur.next  = node
            node.next = self.head
        self.ukuran += 1

    def berikutnya(self):
        """Putar ke format berikutnya."""
        if self.current:
            self.current = self.current.next
        return self.current.format_nama if self.current else None

    def semua_format(self):
        if not self.head:
            return []
        hasil, cur = [], self.head
        for _ in range(self.ukuran):
            hasil.append(cur.format_nama)
            cur = cur.next
        return hasil


# ══════════════════════════════════════════════════════
# STACK — riwayat laporan yang sudah dibuat
# ══════════════════════════════════════════════════════

class Stack:
    def __init__(self):
        self._data = []

    def push(self, item):  self._data.append(item)
    def pop(self):         return self._data.pop() if self._data else None
    def peek(self):        return self._data[-1] if self._data else None
    def kosong(self):      return len(self._data) == 0
    def ukuran(self):      return len(self._data)
    def semua(self):       return list(self._data)


# ══════════════════════════════════════════════════════
# QUEUE — antrian bagian yang akan dicetak
# ══════════════════════════════════════════════════════

class Queue:
    def __init__(self):
        self._data = []

    def enqueue(self, item): self._data.append(item)
    def dequeue(self):       return self._data.pop(0) if self._data else None
    def kosong(self):        return len(self._data) == 0
    def ukuran(self):        return len(self._data)
    def semua(self):         return list(self._data)


# ══════════════════════════════════════════════════════
# HASH TABLE — index cepat ke bagian laporan
# ══════════════════════════════════════════════════════

class HashTable:
    def __init__(self, kapasitas=64):
        self.kapasitas = kapasitas
        self.bucket    = [[] for _ in range(kapasitas)]

    def _hash(self, kunci):
        return sum(ord(c) * (i + 1) for i, c in enumerate(kunci)) % self.kapasitas

    def set(self, kunci, nilai):
        idx = self._hash(kunci)
        for i, (k, _) in enumerate(self.bucket[idx]):
            if k == kunci:
                self.bucket[idx][i] = (kunci, nilai)
                return
        self.bucket[idx].append((kunci, nilai))

    def get(self, kunci):
        for k, v in self.bucket[self._hash(kunci)]:
            if k == kunci:
                return v
        return None

    def ada(self, kunci):
        return self.get(kunci) is not None


# ══════════════════════════════════════════════════════
# TREE — hierarki struktur laporan
# ══════════════════════════════════════════════════════

class TreeNode:
    def __init__(self, nama, urutan=0):
        self.nama     = nama
        self.urutan   = urutan
        self.children = []
        self.isi      = []    # baris konten di bagian ini

    def tambah_child(self, child):
        self.children.append(child)
        return child

    def tambah_isi(self, baris):
        self.isi.append(baris)


def buat_pohon_laporan():
    """
    Hierarki struktur laporan FinSight.

    Laporan FinSight
    ├── 1. Halaman Muka
    │   ├── Identitas perusahaan
    │   └── Tanggal & parameter analisis
    ├── 2. Ringkasan Eksekutif
    │   ├── Graham Scorecard
    │   ├── Risk Level
    │   └── Rekomendasi
    ├── 3. Rasio Keuangan
    │   ├── Likuiditas
    │   ├── Profitabilitas
    │   ├── Solvabilitas
    │   ├── Aktivitas
    │   └── Pasar
    ├── 4. Analisis Graham
    │   ├── Valuasi (Graham Number, EPV, DCF)
    │   ├── 7 Kriteria Defensive
    │   ├── NCAV Test
    │   ├── Earnings Quality
    │   ├── Balance Sheet
    │   └── Dividend
    ├── 5. Analisis Risiko
    │   ├── Risk Dashboard
    │   ├── Altman Z-Score
    │   ├── Springate S-Score
    │   ├── Beneish M-Score
    │   └── Red Flags
    └── 6. Kesimpulan & Rekomendasi
        ├── Grade & Skor Final
        └── Catatan Analis
    """
    root = TreeNode("Laporan FinSight", urutan=0)

    b1 = root.tambah_child(TreeNode("Halaman Muka",          urutan=1))
    b1.tambah_child(TreeNode("Identitas Perusahaan",          urutan=1))
    b1.tambah_child(TreeNode("Parameter Analisis",            urutan=2))

    b2 = root.tambah_child(TreeNode("Ringkasan Eksekutif",    urutan=2))
    b2.tambah_child(TreeNode("Graham Scorecard",              urutan=1))
    b2.tambah_child(TreeNode("Risk Level",                    urutan=2))
    b2.tambah_child(TreeNode("Rekomendasi",                   urutan=3))

    b3 = root.tambah_child(TreeNode("Rasio Keuangan",         urutan=3))
    for i, nama in enumerate(["Likuiditas","Profitabilitas",
                               "Solvabilitas","Aktivitas","Pasar"], 1):
        b3.tambah_child(TreeNode(nama, urutan=i))

    b4 = root.tambah_child(TreeNode("Analisis Graham",        urutan=4))
    for i, nama in enumerate(["Valuasi","7 Kriteria",
                               "NCAV","Earnings Quality",
                               "Balance Sheet","Dividend"], 1):
        b4.tambah_child(TreeNode(nama, urutan=i))

    b5 = root.tambah_child(TreeNode("Analisis Risiko",        urutan=5))
    for i, nama in enumerate(["Dashboard","Altman Z",
                               "Springate S","Beneish M","Red Flags"], 1):
        b5.tambah_child(TreeNode(nama, urutan=i))

    b6 = root.tambah_child(TreeNode("Kesimpulan",             urutan=6))
    b6.tambah_child(TreeNode("Grade & Skor Final",            urutan=1))
    b6.tambah_child(TreeNode("Catatan Analis",                urutan=2))

    return root


def cetak_pohon_rekursif(node, lines, indent=0):
    """Cetak pohon laporan secara rekursif ke list lines."""
    prefix = "  " * indent
    if node.urutan > 0:
        lines.append(f"{prefix}{node.urutan}. {node.nama}")
    else:
        lines.append(f"{prefix}{node.nama}")
    for child in node.children:
        cetak_pohon_rekursif(child, lines, indent + 1)


def hitung_total_bagian_rekursif(node, count=0):
    """Hitung total bagian dalam pohon secara rekursif."""
    if node.urutan > 0:
        count += 1
    for child in node.children:
        count = hitung_total_bagian_rekursif(child, count)
    return count


# ══════════════════════════════════════════════════════
# REKURSIF — ringkasan dan rata-rata
# ══════════════════════════════════════════════════════

def rata_rata_rekursif(data, index=0, total=0.0):
    if not data:
        return 0.0
    if index == len(data):
        return total / len(data)
    return rata_rata_rekursif(data, index + 1, total + data[index])


def cari_nilai_rekursif(data_list, kunci, index=0):
    """Cari nilai pertama yang cocok secara rekursif."""
    if index >= len(data_list):
        return None
    if isinstance(data_list[index], dict) and kunci in data_list[index]:
        return data_list[index][kunci]
    return cari_nilai_rekursif(data_list, kunci, index + 1)


def gabung_baris_rekursif(baris_list, index=0, hasil=""):
    """Gabungkan list baris menjadi satu string secara rekursif."""
    if index >= len(baris_list):
        return hasil
    return gabung_baris_rekursif(
        baris_list, index + 1,
        hasil + baris_list[index] + "\n"
    )


def hitung_lulus_rekursif(kriteria_dict, keys, index=0, count=0):
    """Hitung jumlah kriteria yang lulus secara rekursif."""
    if index >= len(keys):
        return count
    tambah = 1 if kriteria_dict.get(keys[index], False) else 0
    return hitung_lulus_rekursif(kriteria_dict, keys, index + 1, count + tambah)


# ══════════════════════════════════════════════════════
# KELAS UTAMA
# ══════════════════════════════════════════════════════

class Reporter:
    """
    Menyatukan hasil RatioEngine, GrahamAnalyzer, RiskAnalyzer
    menjadi laporan final.

    Contoh:
        reporter = Reporter(data)
        reporter.buat_laporan()
        reporter.simpan("txt")
        reporter.simpan("json")
    """

    def __init__(self, data: CompanyData,
                 ratio_engine:    RatioEngine    = None,
                 graham_analyzer: GrahamAnalyzer = None,
                 risk_analyzer:   RiskAnalyzer   = None):

        self.data    = data
        self.ticker  = data.profil.ticker

        # modul analisis — jalankan jika belum ada
        self.ratio   = ratio_engine    or RatioEngine(data)
        self.graham  = graham_analyzer or GrahamAnalyzer(data)
        self.risk    = risk_analyzer   or RiskAnalyzer(data)

        # struktur data
        self.bagian      = SingleLinkedList()
        self.navigasi    = DoubleLinkedList()
        self.format_rotasi = CircularLinkedList()
        self.riwayat     = Stack()
        self.antrian     = Queue()
        self.index       = HashTable()
        self.pohon       = buat_pohon_laporan()

        # hasil
        self.baris_laporan: list  = []    # semua baris teks laporan
        self.data_laporan:  dict  = {}    # data terstruktur untuk JSON
        self.bagian_selesai: set  = set()
        self.metadata:      dict  = {}

        # daftarkan format output ke CLL
        for fmt in ["txt", "json"]:
            self.format_rotasi.tambah(fmt)

    # ──────────────────────────────────────────────────
    # TITIK MASUK
    # ──────────────────────────────────────────────────

    def buat_laporan(self):
        """
        Jalankan semua analisis lalu susun laporan lengkap.
        """
        print(f"\n  Menyusun laporan — {self.ticker}...")

        # pastikan semua modul sudah dijalankan
        if not self.ratio.semua_rasio:
            self.ratio.hitung_semua()
        if not self.graham.scorecard:
            self.graham.analisis()
        if not self.risk.dashboard:
            self.risk.analisis()

        # isi metadata
        self.metadata = {
            "ticker":   self.ticker,
            "nama":     self.data.profil.nama,
            "sektor":   self.data.profil.sektor,
            "harga":    self.data.profil.harga_pasar,
            "periode":  self.data.tahun_tersedia(),
            "tanggal":  datetime.today().strftime(cfg.CLI["date_format"]),
            "versi":    cfg.APP_VERSION,
        }

        # antrian bagian laporan
        for bagian in ["halaman_muka", "ringkasan", "rasio",
                        "graham", "risiko", "kesimpulan"]:
            self.antrian.enqueue(bagian)

        urutan = 1
        while not self.antrian.kosong():
            bagian = self.antrian.dequeue()
            self.riwayat.push(f"buat:{bagian}")

            if bagian == "halaman_muka":
                konten = self._buat_halaman_muka()
            elif bagian == "ringkasan":
                konten = self._buat_ringkasan()
            elif bagian == "rasio":
                konten = self._buat_rasio()
            elif bagian == "graham":
                konten = self._buat_graham()
            elif bagian == "risiko":
                konten = self._buat_risiko()
            elif bagian == "kesimpulan":
                konten = self._buat_kesimpulan()
            else:
                konten = []

            # simpan ke SLL dan DLL
            judul = bagian.replace("_", " ").title()
            self.bagian.tambah(urutan, judul, konten)
            self.navigasi.tambah(urutan, judul, konten)

            # index ke hash table
            self.index.set(bagian, urutan)

            # tandai selesai (set)
            self.bagian_selesai.add(bagian)

            # tambah ke baris laporan
            self.baris_laporan.extend(konten)

            urutan += 1

        # susun data JSON
        self._susun_data_json()

        print(f"  Laporan selesai — {self.bagian.ukuran()} bagian, "
              f"{len(self.baris_laporan)} baris.")
        return self

    # ──────────────────────────────────────────────────
    # BAGIAN 1 — HALAMAN MUKA
    # ──────────────────────────────────────────────────

    def _buat_halaman_muka(self):
        p  = self.data.profil
        b  = []
        lebar = 60

        b.append(_garis("=", lebar))
        b.append(f"  LAPORAN ANALISIS FUNDAMENTAL")
        b.append(f"  VALUE INVESTING — METODE BENJAMIN GRAHAM")
        b.append(_garis("=", lebar))
        b.append(f"  Perusahaan : {p.nama}")
        b.append(f"  Ticker     : {p.ticker}")
        b.append(f"  Sektor     : {p.sektor}")
        b.append(f"  Harga      : Rp {p.harga_pasar:,.0f}")
        b.append(f"  Periode    : "
                 f"{', '.join(map(str, self.data.tahun_tersedia()))}")
        b.append(f"  Tanggal    : {self.metadata['tanggal']}")
        b.append(f"  Versi      : FinSight CLI v{cfg.APP_VERSION}")
        b.append(_garis("=", lebar))
        b.append("")

        # struktur laporan dari pohon (rekursif)
        b.append("  DAFTAR ISI")
        b.append(_garis("-", lebar))
        lines = []
        cetak_pohon_rekursif(self.pohon, lines, indent=1)
        b.extend(["  " + l for l in lines])
        b.append("")

        return b

    # ──────────────────────────────────────────────────
    # BAGIAN 2 — RINGKASAN EKSEKUTIF
    # ──────────────────────────────────────────────────

    def _buat_ringkasan(self):
        b = []
        b.append(_garis("="))
        b.append("  2. RINGKASAN EKSEKUTIF")
        b.append(_garis("="))
        b.append("")

        # Graham Scorecard
        total_skor = self.graham.scorecard.get("total_skor", 0)
        grade      = self.graham.scorecard.get("grade", "?")
        label      = self.graham.scorecard.get("label", "")

        b.append("  GRAHAM SCORECARD")
        b.append(_garis("-"))
        skor_komponen = self.graham.scorecard.get("skor_per_komponen", {})

        # sorting komponen dari tertinggi ke terendah
        terurut = sorted(skor_komponen.items(), key=lambda x: x[1], reverse=True)
        for nama, skor in terurut:
            bobot = cfg.SCORECARD_WEIGHTS.get(nama, 0)
            bar   = "█" * (skor // 10) + "░" * (10 - skor // 10)
            b.append(f"  {nama:<28}: {skor:>3}/100  {bar}  [{bobot*100:.0f}%]")

        b.append(_garis("-"))
        b.append(f"  {'TOTAL SKOR':<28}: {total_skor:>3}/100")
        b.append(f"  {'GRADE':<28}: {grade} — {label}")
        b.append("")

        # Risk Level
        total_risk = self.risk.dashboard.get("total", {})
        skor_risk  = total_risk.get("skor_risiko", 0)
        level_risk = total_risk.get("level", "-")
        n_flags    = len(self.risk.red_flags)

        b.append("  RISK DASHBOARD")
        b.append(_garis("-"))
        b.append(f"  {'Total Risk Score':<28}: {skor_risk:>3}/100  [{level_risk}]")
        b.append(f"  {'Red Flags':<28}: {n_flags} ditemukan")

        # skor per kategori (sorting)
        for kat, sk in self.risk.urutkan_kategori_by_risiko():
            bar = "█" * (sk // 10) + "░" * (10 - sk // 10)
            b.append(f"  {kat:<28}: {sk:>3}  {bar}")
        b.append("")

        # Valuasi ringkas
        harga = self.data.profil.harga_pasar
        gn    = self.graham.valuasi.get("graham_number", 0)
        epv   = self.graham.valuasi.get("epv_per_saham", 0)
        dcf   = self.graham.valuasi.get("dcf_per_saham", 0)
        ni    = self.graham.valuasi.get("nilai_intrinsik_konservatif", 0)
        mos   = self.graham.valuasi.get("margin_of_safety_final", 0)
        rek   = self.graham.valuasi.get("rekomendasi_mos", "-")

        b.append("  VALUASI RINGKAS")
        b.append(_garis("-"))
        for label_v, nilai in [
            ("Graham Number",   gn),
            ("EPV per Saham",   epv),
            ("DCF per Saham",   dcf),
            ("Nilai Intrinsik", ni),
            ("Harga Pasar",     harga),
        ]:
            b.append(f"  {label_v:<28}: Rp {nilai:>12,.0f}")
        b.append(f"  {'Margin of Safety':<28}: {mos*100:>7.1f}%")
        b.append(f"  {'Rekomendasi':<28}: {rek}")
        b.append("")

        return b

    # ──────────────────────────────────────────────────
    # BAGIAN 3 — RASIO KEUANGAN
    # ──────────────────────────────────────────────────

    def _buat_rasio(self):
        b = []
        b.append(_garis("="))
        b.append("  3. RASIO KEUANGAN")
        b.append(_garis("="))
        b.append("")

        tahun_list = self.data.tahun_tersedia()

        # header tabel
        header = f"  {'Rasio':<28}"
        for t in tahun_list:
            header += f"  {t:>8}"
        b.append(header)

        # cetak per kategori dari pohon
        for cat_node in self.ratio.pohon_kategori.children:
            b.append("")
            b.append(f"  [{cat_node.nama}]")
            b.append("  " + _garis("-", 28 + len(tahun_list) * 10))

            for nama_rasio in cat_node.rasio:
                meta  = cfg.RATIO_META.get(nama_rasio, {})
                label = meta.get("name", nama_rasio)
                unit  = meta.get("unit", "")
                baris = f"  {label:<28}"

                for tahun in tahun_list:
                    node = self.ratio.rasio_per_tahun.cari_tahun(tahun)
                    nilai = node.rasio.get(nama_rasio, 0) if node else 0

                    if unit == "%":
                        baris += f"  {nilai*100:>7.1f}%"
                    else:
                        baris += f"  {nilai:>8.2f}"
                b.append(baris)

        b.append("")

        # CAGR ringkas
        b.append("  CAGR (Compound Annual Growth Rate)")
        b.append(_garis("-"))
        for kunci, label in [
            ("cagr_pendapatan", "CAGR Pendapatan"),
            ("cagr_laba",       "CAGR Laba Bersih"),
            ("cagr_fcf",        "CAGR Free Cash Flow"),
        ]:
            nilai = self.ratio.ringkasan.get(kunci, 0)
            if nilai:
                b.append(f"  {label:<28}: {nilai*100:>7.2f}%")
        b.append("")

        return b

    # ──────────────────────────────────────────────────
    # BAGIAN 4 — ANALISIS GRAHAM
    # ──────────────────────────────────────────────────

    def _buat_graham(self):
        b = []
        b.append(_garis("="))
        b.append("  4. ANALISIS GRAHAM — VALUE INVESTING")
        b.append(_garis("="))
        b.append("")

        # 4a. Valuasi detail
        harga = self.data.profil.harga_pasar
        b.append("  4a. VALUASI MULTI-METODE")
        b.append(_garis("-"))
        for kunci, label, unit in [
            ("graham_number",               "Graham Number",          "Rp"),
            ("epv_per_saham",               "EPV per Saham",          "Rp"),
            ("dcf_per_saham",               "DCF per Saham",          "Rp"),
            ("nilai_intrinsik_konservatif",  "Nilai Intrinsik (min)",  "Rp"),
            ("margin_of_safety_final",       "Margin of Safety Final", "%"),
            ("wacc_digunakan",               "WACC",                   "%"),
            ("growth_digunakan",             "Growth Rate",            "%"),
        ]:
            nilai = self.graham.valuasi.get(kunci, 0)
            if unit == "%":
                b.append(f"  {label:<32}: {nilai*100:>7.2f}%")
            else:
                b.append(f"  {label:<32}: Rp {nilai:>12,.0f}")
        b.append(f"  {'Harga Pasar':<32}: Rp {harga:>12,.0f}")
        b.append(f"  {'Rekomendasi':<32}: "
                 f"{self.graham.valuasi.get('rekomendasi_mos','')}")
        b.append("")

        # 4b. Tren Graham Number historis (dari DLL)
        b.append("  4b. TREN GRAHAM NUMBER & MoS HISTORIS")
        b.append(_garis("-"))
        tahun_list = self.data.tahun_tersedia()
        delta      = self.graham.navigasi.perubahan("graham_number")
        for tahun, gn, arah in delta:
            node_mos = self.graham.rantai.cari(tahun)
            mos      = node_mos.hasil.get("margin_of_safety", 0) if node_mos else 0
            b.append(f"  {tahun} | GN: Rp {gn:>10,.0f} | "
                     f"MoS: {mos*100:>6.1f}%  ({arah})")
        b.append("")

        # 4c. 7 Kriteria Defensive Investor
        b.append("  4c. 7 KRITERIA DEFENSIVE INVESTOR")
        b.append(_garis("-"))
        deskripsi = {
            "kriteria_1": "Ukuran perusahaan memadai",
            "kriteria_2": f"Current Ratio >= {cfg.GRAHAM['min_current_ratio']}x",
            "kriteria_3": "Stabilitas laba (tidak rugi)",
            "kriteria_4": f"Dividen konsisten >= {cfg.GRAHAM['min_years_data']} thn",
            "kriteria_5": f"EPS growth >= {cfg.GRAHAM['min_eps_growth_10yr']*100:.0f}%",
            "kriteria_6": f"P/E <= {cfg.GRAHAM['max_pe_ratio']}x",
            "kriteria_7": f"P/BV <= {cfg.GRAHAM['max_pb_ratio']}x",
        }
        kriteria = self.graham.scorecard.get("kriteria_7", {})
        keys     = list(kriteria.keys())

        # hitung lulus rekursif
        n_lulus  = hitung_lulus_rekursif(kriteria, keys)
        for nama, lulus in kriteria.items():
            tanda = "LULUS" if lulus else "GAGAL"
            desc  = deskripsi.get(nama, nama)
            b.append(f"  [{tanda}] {desc}")
        skor_k7  = self.graham.scorecard.get("skor_kriteria_7", 0)
        total_k7 = self.graham.scorecard.get("total_kriteria_7", 7)
        b.append(f"  Skor: {skor_k7}/{total_k7} "
                 f"({n_lulus} lulus dari {total_k7} kriteria)")
        b.append("")

        # 4d. NCAV
        ncav_data = self.graham.scorecard.get("ncav", {})
        b.append("  4d. NCAV / CIGAR BUTT TEST")
        b.append(_garis("-"))
        for k, label in [
            ("ncav_per_saham", "NCAV per Saham"),
            ("nnwc_per_saham", "NNWC per Saham (konservatif)"),
            ("harga_vs_ncav",  "Harga / NCAV"),
        ]:
            val = ncav_data.get(k, 0)
            if k == "harga_vs_ncav":
                b.append(f"  {label:<32}: {val:.2f}x")
            else:
                b.append(f"  {label:<32}: Rp {val:>12,.2f}")
        b.append(f"  {'Status':<32}: {ncav_data.get('status', '-')}")
        b.append("")

        # 4e. Earnings Quality
        eq = self.graham.scorecard.get("earnings_quality", {})
        b.append("  4e. KUALITAS LABA")
        b.append(_garis("-"))
        for k, label, unit in [
            ("konsistensi_laba",  "Konsistensi Laba",     "%"),
            ("accrual_ratio",     "Accrual Ratio",        "%"),
            ("cagr_eps",          "CAGR EPS",             "%"),
            ("cv_eps",            "Volatilitas EPS (CV)",  "%"),
            ("kualitas_accrual",  "Kualitas Accrual",     ""),
            ("stabilitas_eps",    "Stabilitas EPS",       ""),
        ]:
            val = eq.get(k, 0)
            if unit == "%":
                b.append(f"  {label:<32}: {val*100:>7.2f}%")
            else:
                b.append(f"  {label:<32}: {val}")
        b.append("")

        # 4f. Balance Sheet Strength
        bs = self.graham.scorecard.get("balance_sheet", {})
        b.append("  4f. KEKUATAN NERACA")
        b.append(_garis("-"))
        for k, label in [
            ("working_capital",       "Working Capital"),
            ("tangible_book_value",   "Tangible Book Value"),
            ("tangible_bv_per_saham", "Tangible BV per Saham"),
            ("net_debt",              "Net Debt"),
        ]:
            val = bs.get(k, 0)
            b.append(f"  {label:<32}: Rp {val:>12,.0f}")
        for k, label in [
            ("der",               "Debt-to-Equity"),
            ("interest_coverage", "Interest Coverage"),
            ("ltd_vs_nca",        "LT Debt / Net Current Assets"),
        ]:
            val = bs.get(k, 0)
            ok  = bs.get(k + "_ok", None)
            tanda = " [OK]" if ok else (" [!]" if ok is False else "")
            b.append(f"  {label:<32}: {val:>8.2f}x{tanda}")
        b.append("")

        # 4g. Dividend
        div = self.graham.scorecard.get("dividend", {})
        b.append("  4g. KONSISTENSI DIVIDEN")
        b.append(_garis("-"))
        b.append(f"  {'Tahun Bayar Dividen':<32}: "
                 f"{div.get('tahun_bayar_dividen',0)} / "
                 f"{div.get('total_tahun_data',0)} tahun")
        b.append(f"  {'Payout Ratio':<32}: "
                 f"{div.get('payout_ratio',0)*100:.1f}%  "
                 f"{'[OK]' if div.get('payout_ok') else '[!]'}")
        b.append(f"  {'Dividend Coverage':<32}: "
                 f"{div.get('dividend_coverage',0):.2f}x  "
                 f"{'[OK]' if div.get('coverage_ok') else '[!]'}")
        b.append(f"  {'CAGR Dividen':<32}: "
                 f"{div.get('cagr_dps',0)*100:.2f}%")
        b.append("")

        return b

    # ──────────────────────────────────────────────────
    # BAGIAN 5 — ANALISIS RISIKO
    # ──────────────────────────────────────────────────

    def _buat_risiko(self):
        b = []
        b.append(_garis("="))
        b.append("  5. ANALISIS RISIKO KEUANGAN")
        b.append(_garis("="))
        b.append("")

        # 5a. Dashboard
        total = self.risk.dashboard.get("total", {})
        b.append("  5a. RISK DASHBOARD")
        b.append(_garis("-"))
        b.append(f"  {'Total Risk Score':<28}: "
                 f"{total.get('skor_risiko',0):>3}/100  "
                 f"[{total.get('level','-')}]")
        b.append(f"  {'Tren Risiko':<28}: {total.get('tren','-')}")
        b.append(f"  {'Jumlah Red Flag':<28}: {total.get('jumlah_red_flag',0)}")
        b.append("")

        # skor per kategori (sorting)
        b.append("  Skor per Kategori (tertinggi → terendah):")
        for kat, sk in self.risk.urutkan_kategori_by_risiko():
            bar = "█" * (sk // 10) + "░" * (10 - sk // 10)
            b.append(f"  {kat:<25}: {sk:>3}  {bar}")
        b.append("")

        # 5b. Scoring models
        for kunci, nomor, judul, fields in [
            ("altman_z",    "5b", "ALTMAN Z-SCORE",
             [("z_score","Z-Score","float"),("status","Status","str"),
              ("x1","X1 (WC/TA)","float"),("x2","X2 (RE/TA)","float"),
              ("x3","X3 (EBIT/TA)","float"),("x4","X4 (MC/TL)","float"),
              ("x5","X5 (Rev/TA)","float")]),
            ("springate_s", "5c", "SPRINGATE S-SCORE",
             [("s_score","S-Score","float"),("status","Status","str"),
              ("a","A (WC/TA)","float"),("b","B (EBIT/TA)","float"),
              ("c","C (EBT/TLL)","float"),("d","D (Rev/TA)","float")]),
            ("beneish_m",   "5d", "BENEISH M-SCORE (Deteksi Manipulasi)",
             [("m_score","M-Score","float"),("status","Status","str"),
              ("dsri","DSRI","float"),("gmi","GMI","float"),
              ("aqi","AQI","float"),("sgi","SGI","float"),
              ("tata","TATA","float")]),
        ]:
            detail = self.risk.dashboard.get(kunci, {})
            b.append(f"  {nomor}. {judul}")
            b.append(_garis("-"))
            for field, label, tipe in fields:
                val = detail.get(field)
                if val is None:
                    continue
                if tipe == "float":
                    b.append(f"  {label:<28}: {val:>10.4f}")
                else:
                    b.append(f"  {label:<28}: {val}")
            b.append("")

        # 5e. Red Flags (sorting berdasarkan urutan)
        b.append("  5e. RED FLAGS")
        b.append(_garis("-"))
        if self.risk.red_flags:
            for i, flag in self.risk.ranking_red_flags():
                b.append(f"  [{i}] {flag}")
        else:
            b.append("  Tidak ada red flag ditemukan.")
        b.append("")

        # 5f. Tren historis (DLL)
        b.append("  5f. TREN RISIKO HISTORIS")
        b.append(_garis("-"))
        tren_cr  = self.risk.navigasi.perubahan("current_ratio")
        tren_der = self.risk.navigasi.perubahan("der")
        header   = f"  {'Tahun':<6} | {'CR':>6} | {'DER':>6} | {'Altman Z':>10} | Arah CR"
        b.append(header)
        b.append("  " + "-" * 50)
        for (t, cr, arah_cr), (_, der, _) in zip(tren_cr, tren_der):
            node_z = self.risk.rantai.cari(t)
            z_val  = node_z.skor.get("altman_z", 0) if node_z else 0
            b.append(f"  {t:<6} | {cr:>6.2f} | {der:>6.2f} | "
                     f"{z_val:>10.2f} | {arah_cr}")
        b.append("")

        return b

    # ──────────────────────────────────────────────────
    # BAGIAN 6 — KESIMPULAN & REKOMENDASI
    # ──────────────────────────────────────────────────

    def _buat_kesimpulan(self):
        b = []
        b.append(_garis("="))
        b.append("  6. KESIMPULAN & REKOMENDASI")
        b.append(_garis("="))
        b.append("")

        grade      = self.graham.scorecard.get("grade", "?")
        label      = self.graham.scorecard.get("label", "")
        total_skor = self.graham.scorecard.get("total_skor", 0)
        risk_level = self.risk.dashboard.get("total", {}).get("level", "-")
        rek        = self.graham.valuasi.get("rekomendasi_mos", "-")
        mos        = self.graham.valuasi.get("margin_of_safety_final", 0)
        harga      = self.data.profil.harga_pasar
        ni         = self.graham.valuasi.get("nilai_intrinsik_konservatif", 0)
        n_flags    = len(self.risk.red_flags)
        skor_k7    = self.graham.scorecard.get("skor_kriteria_7", 0)

        b.append("  GRADE & SKOR FINAL")
        b.append(_garis("-"))
        b.append(f"  Graham Scorecard  : {total_skor}/100  —  Grade {grade} ({label})")
        b.append(f"  Risk Level        : {risk_level}")
        b.append(f"  Red Flags         : {n_flags} ditemukan")
        b.append(f"  7 Kriteria Graham : {skor_k7}/7 lulus")
        b.append(f"  Nilai Intrinsik   : Rp {ni:,.0f}")
        b.append(f"  Harga Pasar       : Rp {harga:,.0f}")
        b.append(f"  Margin of Safety  : {mos*100:.1f}%")
        b.append(f"  Rekomendasi       : {rek}")
        b.append("")

        # catatan analis berdasarkan grade
        b.append("  CATATAN ANALIS")
        b.append(_garis("-"))
        catatan = self._buat_catatan(grade, risk_level, mos, n_flags, skor_k7)
        for baris in catatan:
            b.append(f"  {baris}")
        b.append("")

        # ranking komponen scorecard (sorting)
        b.append("  RANKING KOMPONEN SCORECARD")
        b.append(_garis("-"))
        for nama, skor in self.graham.ranking_komponen():
            bobot = cfg.SCORECARD_WEIGHTS.get(nama, 0)
            b.append(f"  {nama:<30}: {skor:>3}/100  [{bobot*100:.0f}%]")
        b.append("")

        # disclaimer
        b.append(_garis("-"))
        b.append("  DISCLAIMER")
        b.append(_garis("-"))
        b.append("  Laporan ini dibuat secara otomatis oleh FinSight CLI.")
        b.append("  Bukan merupakan saran investasi. Keputusan investasi")
        b.append("  sepenuhnya menjadi tanggung jawab investor.")
        b.append("  Selalu lakukan riset mandiri sebelum berinvestasi.")
        b.append(_garis("="))
        b.append("")

        return b

    def _buat_catatan(self, grade, risk_level, mos, n_flags, skor_k7):
        """Buat catatan analis berdasarkan kondisi fundamental."""
        catatan = []

        if grade in ("A", "B") and risk_level in ("RENDAH", "SEDANG"):
            catatan.append("Perusahaan memiliki fundamental yang kuat dengan")
            catatan.append("risiko yang terkendali.")
        elif grade in ("C",) and risk_level == "RENDAH":
            catatan.append("Fundamental cukup baik namun valuasi belum")
            catatan.append("menarik. Perlu kesabaran menunggu harga turun.")
        elif grade in ("D", "F"):
            catatan.append("Fundamental lemah. Tidak direkomendasikan untuk")
            catatan.append("value investor konservatif ala Graham.")
        else:
            catatan.append("Perlu analisis lebih mendalam sebelum mengambil")
            catatan.append("keputusan investasi.")

        if mos >= cfg.GRAHAM["min_margin_of_safety"]:
            catatan.append(f"Margin of Safety {mos*100:.1f}% memenuhi syarat Graham (>=33%).")
        else:
            catatan.append(f"Margin of Safety {mos*100:.1f}% belum memenuhi syarat Graham.")

        if skor_k7 >= 6:
            catatan.append(f"{skor_k7}/7 kriteria Graham terpenuhi — defensif kuat.")
        elif skor_k7 >= 4:
            catatan.append(f"{skor_k7}/7 kriteria Graham terpenuhi — moderat.")
        else:
            catatan.append(f"Hanya {skor_k7}/7 kriteria Graham terpenuhi — hati-hati.")

        if n_flags > 0:
            catatan.append(f"Ditemukan {n_flags} red flag — perlu perhatian khusus.")

        return catatan

    # ──────────────────────────────────────────────────
    # SUSUN DATA JSON
    # ──────────────────────────────────────────────────

    def _susun_data_json(self):
        """Susun seluruh data laporan ke dalam dict untuk JSON."""
        self.data_laporan = {
            "metadata":   self.metadata,
            "scorecard":  self.graham.scorecard.get("skor_per_komponen", {}),
            "grade":      self.graham.scorecard.get("grade", ""),
            "label":      self.graham.scorecard.get("label", ""),
            "total_skor": self.graham.scorecard.get("total_skor", 0),
            "valuasi":    self.graham.valuasi,
            "kriteria_7": self.graham.scorecard.get("kriteria_7", {}),
            "ncav":       self.graham.scorecard.get("ncav", {}),
            "earnings_quality": self.graham.scorecard.get("earnings_quality", {}),
            "balance_sheet":    self.graham.scorecard.get("balance_sheet", {}),
            "dividend":         self.graham.scorecard.get("dividend", {}),
            "risk_dashboard":   {
                k: v for k, v in self.risk.dashboard.items()
                if k != "beneish_m" or isinstance(v, dict)
            },
            "red_flags":  self.risk.red_flags,
            "rasio_terbaru": (
                self.ratio.semua_rasio[-1]
                if self.ratio.semua_rasio else {}
            ),
            "historis_rasio":  self.ratio.semua_rasio,
            "historis_graham": self.graham.hasil_per_tahun,
            "historis_risiko": self.risk.hasil_per_tahun,
        }

    # ──────────────────────────────────────────────────
    # SEARCHING — cari bagian laporan
    # ──────────────────────────────────────────────────

    def cari_bagian(self, kata_kunci):
        """
        Cari bagian laporan berdasarkan kata kunci.
        Menggunakan SLL untuk traversal.
        """
        return self.bagian.cari_judul(kata_kunci)

    def cari_urutan(self, nama_bagian):
        """Cari nomor urut bagian via Hash Table O(1)."""
        return self.index.get(nama_bagian)

    # ──────────────────────────────────────────────────
    # SORTING — urutkan temuan
    # ──────────────────────────────────────────────────

    def red_flags_terurut(self):
        """Kembalikan red flags sebagai list tuple terurut."""
        return [(i + 1, flag) for i, flag in enumerate(self.risk.red_flags)]

    def komponen_terurut(self):
        """Urutkan komponen scorecard dari tertinggi."""
        skor = self.graham.scorecard.get("skor_per_komponen", {})
        return sorted(skor.items(), key=lambda x: x[1], reverse=True)

    # ──────────────────────────────────────────────────
    # FILE HANDLER — simpan laporan
    # ──────────────────────────────────────────────────

    def simpan(self, format_file="txt"):
        """
        Simpan laporan ke file.
        Format: 'txt' atau 'json'
        """
        tanggal   = datetime.today().strftime(cfg.OUTPUT_DATE_FORMAT)
        nama_file = f"{self.ticker}_laporan_{tanggal}.{format_file}"
        path      = cfg.OUTPUTS_DIR / nama_file

        if format_file == "json":
            self._simpan_json(path)
        else:
            self._simpan_txt(path)

        self.riwayat.push(f"simpan:{format_file}:{path}")
        print(f"  Laporan disimpan: {path}")
        return path

    def _simpan_txt(self, path):
        """Tulis semua baris laporan ke file teks."""
        teks = gabung_baris_rekursif(self.baris_laporan)
        with open(path, "w", encoding="utf-8") as f:
            f.write(teks)

    def _simpan_json(self, path):
        """Tulis data laporan ke file JSON."""
        def bersihkan(obj):
            if isinstance(obj, dict):
                return {k: bersihkan(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [bersihkan(v) for v in obj]
            if isinstance(obj, (int, float, str, bool)) or obj is None:
                return obj
            return str(obj)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(bersihkan(self.data_laporan), f,
                      indent=2, ensure_ascii=False)

    def baca_laporan(self, path):
        """File Handler — baca laporan JSON yang sudah disimpan."""
        path = Path(path)
        if not path.exists():
            print(f"  ERROR: File tidak ditemukan — {path}")
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"  ERROR: {e}")
            return None

    # ──────────────────────────────────────────────────
    # TAMPILKAN DI TERMINAL
    # ──────────────────────────────────────────────────

    def tampilkan(self):
        """Cetak laporan lengkap ke terminal."""
        # cetak baris per baris dari antrian bagian (via DLL)
        cur = self.navigasi.bagian_pertama()
        while cur:
            for baris in cur.konten:
                print(baris)
            cur = self.navigasi.maju(cur)

    def tampilkan_ringkasan(self):
        """Cetak hanya ringkasan eksekutif."""
        node = self.cari_bagian("ringkasan")
        if node:
            for baris in node.konten:
                print(baris)

    def info_laporan(self):
        """Cetak info laporan yang sudah dibuat."""
        print()
        print(f"  Laporan   : {self.data.profil.nama} ({self.ticker})")
        print(f"  Bagian    : {self.bagian.ukuran()}")
        print(f"  Baris     : {len(self.baris_laporan)}")
        print(f"  Format    : {self.format_rotasi.semua_format()}")
        print(f"  Riwayat   : {self.riwayat.ukuran()} operasi")
        print(f"  Selesai   : {self.bagian_selesai}")
        total_bagian = hitung_total_bagian_rekursif(self.pohon)
        print(f"  Pohon     : {total_bagian} sub-bagian terdefinisi")
        print()
