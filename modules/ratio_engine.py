"""
modules/ratio_engine.py
========================
Menghitung semua rasio keuangan dari CompanyData.

Struktur data yang diterapkan:
  - Single Linked List   : rantai RatioNode per tahun
  - Double Linked List   : navigasi maju-mundur antar tahun
  - Circular Linked List : rotasi periode untuk perbandingan
  - Stack                : riwayat operasi perhitungan
  - Queue                : antrian laporan yang akan dicetak
  - Hash Table (dict)    : lookup rasio O(1)
  - Tree                 : kategori rasio bertingkat
  - List / Tuple / Set   : wadah hasil dan kategori unik
  - Sorting              : urutkan rasio dan ranking
  - Searching            : cari rasio dan tahun tertentu
  - Rekursif             : hitung CAGR dan pertumbuhan
  - File Handler         : simpan hasil ke file
  - OOP                  : class RatioEngine
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
from sort_utils import merge_sort


# ══════════════════════════════════════════════════════
# SINGLE LINKED LIST — rantai RatioNode per tahun
# ══════════════════════════════════════════════════════

class RatioNode:
    """Satu node berisi semua rasio untuk satu tahun."""
    def __init__(self, tahun, rasio: dict):
        self.tahun = tahun
        self.rasio = rasio   # { nama_rasio: nilai }
        self.next  = None    # pointer ke tahun berikutnya


class SingleLinkedList:
    """
    Linked list satu arah — setiap node = satu tahun.
    Urutan: tahun terlama → terbaru.
    """
    def __init__(self):
        self.head = None

    def tambah(self, tahun, rasio: dict):
        """Tambah node baru di akhir list."""
        node_baru = RatioNode(tahun, rasio)
        if self.head is None:
            self.head = node_baru
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = node_baru

    def cari_tahun(self, tahun):
        """
        Searching — cari node berdasarkan tahun.
        Return: RatioNode jika ketemu, None jika tidak.
        """
        current = self.head
        while current:
            if current.tahun == tahun:
                return current
            current = current.next
        return None

    def ke_list(self):
        """Konversi linked list ke list Python biasa."""
        hasil = []
        current = self.head
        while current:
            hasil.append(current)
            current = current.next
        return hasil

    def semua_tahun(self):
        return [node.tahun for node in self.ke_list()]


# ══════════════════════════════════════════════════════
# DOUBLE LINKED LIST — navigasi maju-mundur antar tahun
# ══════════════════════════════════════════════════════

class DoubleNode:
    """Node untuk double linked list."""
    def __init__(self, tahun, rasio: dict):
        self.tahun = tahun
        self.rasio = rasio
        self.next  = None
        self.prev  = None


class DoubleLinkedList:
    """
    Linked list dua arah — bisa navigasi maju dan mundur.
    Berguna untuk membandingkan rasio tahun ini vs tahun lalu.
    """
    def __init__(self):
        self.head = None
        self.tail = None

    def tambah(self, tahun, rasio: dict):
        node_baru = DoubleNode(tahun, rasio)
        if self.head is None:
            self.head = node_baru
            self.tail = node_baru
            return
        node_baru.prev = self.tail
        self.tail.next = node_baru
        self.tail       = node_baru

    def terbaru(self):
        """Ambil node tahun terbaru (dari tail)."""
        return self.tail

    def sebelumnya(self, node):
        """Ambil node tahun sebelumnya."""
        return node.prev if node else None

    def delta_rasio(self, nama_rasio):
        """
        Hitung perubahan rasio dari tahun ke tahun.
        Return: list of (tahun, nilai, perubahan)
        """
        hasil = []
        current = self.head
        while current:
            nilai   = current.rasio.get(nama_rasio, 0)
            delta   = 0.0
            if current.prev:
                nilai_lalu = current.prev.rasio.get(nama_rasio, 0)
                if nilai_lalu != 0:
                    delta = (nilai - nilai_lalu) / abs(nilai_lalu)
            hasil.append((current.tahun, nilai, delta))
            current = current.next
        return hasil


# ══════════════════════════════════════════════════════
# CIRCULAR LINKED LIST — rotasi periode analisis
# ══════════════════════════════════════════════════════

class CircularNode:
    def __init__(self, tahun, rasio: dict):
        self.tahun = tahun
        self.rasio = rasio
        self.next  = None


class CircularLinkedList:
    """
    Linked list melingkar — setelah node terakhir kembali ke awal.
    Digunakan untuk rotasi window periode perbandingan.
    """
    def __init__(self):
        self.head  = None
        self.ukuran = 0

    def tambah(self, tahun, rasio: dict):
        node_baru = CircularNode(tahun, rasio)
        if self.head is None:
            self.head      = node_baru
            node_baru.next = self.head
        else:
            current = self.head
            while current.next != self.head:
                current = current.next
            current.next   = node_baru
            node_baru.next = self.head
        self.ukuran += 1

    def window(self, n):
        """
        Ambil n tahun terakhir sebagai window perbandingan.
        Memanfaatkan sifat circular — mulai dari head, putar n langkah.
        """
        if self.head is None or n <= 0:
            return []
        hasil   = []
        current = self.head
        # putar ke posisi (ukuran - n) untuk ambil n terbaru
        langkah = max(0, self.ukuran - n)
        for _ in range(langkah):
            current = current.next
        for _ in range(min(n, self.ukuran)):
            hasil.append((current.tahun, current.rasio))
            current = current.next
        return hasil


# ══════════════════════════════════════════════════════
# STACK — riwayat operasi perhitungan
# ══════════════════════════════════════════════════════

class Stack:
    """
    LIFO — menyimpan riwayat rasio yang sudah dihitung.
    Berguna untuk undo atau audit trail perhitungan.
    """
    def __init__(self):
        self._data = []

    def push(self, item):
        self._data.append(item)

    def pop(self):
        if self.kosong():
            return None
        return self._data.pop()

    def peek(self):
        if self.kosong():
            return None
        return self._data[-1]

    def kosong(self):
        return len(self._data) == 0

    def ukuran(self):
        return len(self._data)


# ══════════════════════════════════════════════════════
# QUEUE — antrian laporan yang akan dicetak / disimpan
# ══════════════════════════════════════════════════════

class Queue:
    """
    FIFO — antrian nama rasio yang akan dilaporkan.
    Rasio masuk dari belakang, keluar dari depan.
    """
    def __init__(self):
        self._data = []

    def enqueue(self, item):
        self._data.append(item)

    def dequeue(self):
        if self.kosong():
            return None
        return self._data.pop(0)

    def kosong(self):
        return len(self._data) == 0

    def ukuran(self):
        return len(self._data)

    def semua(self):
        return list(self._data)


# ══════════════════════════════════════════════════════
# TREE — kategori rasio bertingkat
# ══════════════════════════════════════════════════════

class TreeNode:
    """Node pohon untuk hierarki kategori rasio."""
    def __init__(self, nama):
        self.nama     = nama
        self.children = []
        self.rasio    = []   # daftar nama rasio di kategori ini

    def tambah_child(self, child):
        self.children.append(child)
        return child

    def tambah_rasio(self, nama_rasio):
        self.rasio.append(nama_rasio)


def buat_pohon_rasio():
    """
    Bangun pohon hierarki kategori rasio keuangan.

    Rasio Keuangan
    ├── Likuiditas
    │   ├── current_ratio
    │   ├── quick_ratio
    │   └── cash_ratio
    ├── Profitabilitas
    │   ├── gross_margin
    │   ├── net_margin
    │   ├── roe, roa, roic
    │   └── ebitda_margin
    ├── Solvabilitas
    │   ├── der, dar
    │   ├── interest_coverage
    │   └── net_debt_ebitda
    ├── Aktivitas
    │   ├── asset_turnover
    │   ├── inventory_turnover
    │   └── receivable_days
    └── Pasar
        ├── pe_ratio, pb_ratio
        ├── ev_ebitda
        └── dividend_yield
    """
    root = TreeNode("Rasio Keuangan")

    likuiditas = root.tambah_child(TreeNode("Likuiditas"))
    likuiditas.tambah_rasio("current_ratio")
    likuiditas.tambah_rasio("quick_ratio")
    likuiditas.tambah_rasio("cash_ratio")
    likuiditas.tambah_rasio("days_cash_on_hand")

    profitabilitas = root.tambah_child(TreeNode("Profitabilitas"))
    profitabilitas.tambah_rasio("gross_margin")
    profitabilitas.tambah_rasio("net_margin")
    profitabilitas.tambah_rasio("ebitda_margin")
    profitabilitas.tambah_rasio("roe")
    profitabilitas.tambah_rasio("roa")
    profitabilitas.tambah_rasio("roic")

    solvabilitas = root.tambah_child(TreeNode("Solvabilitas"))
    solvabilitas.tambah_rasio("der")
    solvabilitas.tambah_rasio("dar")
    solvabilitas.tambah_rasio("interest_coverage")
    solvabilitas.tambah_rasio("net_debt_ebitda")

    aktivitas = root.tambah_child(TreeNode("Aktivitas"))
    aktivitas.tambah_rasio("asset_turnover")
    aktivitas.tambah_rasio("inventory_turnover")
    aktivitas.tambah_rasio("receivable_days")
    aktivitas.tambah_rasio("payable_days")

    pasar = root.tambah_child(TreeNode("Pasar"))
    pasar.tambah_rasio("pe_ratio")
    pasar.tambah_rasio("pb_ratio")
    pasar.tambah_rasio("ev_ebitda")
    pasar.tambah_rasio("dividend_yield")
    pasar.tambah_rasio("peg_ratio")

    return root


def cari_kategori(root, nama_rasio):
    """
    Searching pada tree — cari kategori dari sebuah rasio.
    Return: nama kategori atau None.
    """
    for child in root.children:
        if nama_rasio in child.rasio:
            return child.nama
        # cari lebih dalam jika ada sub-child
        for subchild in child.children:
            if nama_rasio in subchild.rasio:
                return f"{child.nama} > {subchild.nama}"
    return None


def tampilkan_pohon(node, indent=0):
    """Cetak pohon rasio secara rekursif."""
    prefix = "  " * indent
    if node.rasio:
        print(f"{prefix}[{node.nama}]")
        for r in node.rasio:
            print(f"{prefix}  - {r}")
    else:
        print(f"{prefix}[{node.nama}]")
    for child in node.children:
        tampilkan_pohon(child, indent + 1)


# ══════════════════════════════════════════════════════
# HASH TABLE — lookup rasio O(1)
# ══════════════════════════════════════════════════════

class HashTable:
    """
    Hash table sederhana dengan separate chaining.
    Digunakan untuk lookup nilai rasio berdasarkan kunci
    format "TICKER_TAHUN_NAMARASIO" dengan kompleksitas O(1).
    """
    def __init__(self, kapasitas=64):
        self.kapasitas = kapasitas
        self.bucket    = [[] for _ in range(kapasitas)]

    def _hash(self, kunci: str) -> int:
        total = 0
        for i, karakter in enumerate(kunci):
            total += ord(karakter) * (i + 1)
        return total % self.kapasitas

    def set(self, kunci: str, nilai):
        idx    = self._hash(kunci)
        bucket = self.bucket[idx]
        for i, (k, v) in enumerate(bucket):
            if k == kunci:
                bucket[i] = (kunci, nilai)
                return
        bucket.append((kunci, nilai))

    def get(self, kunci: str):
        idx    = self._hash(kunci)
        bucket = self.bucket[idx]
        for k, v in bucket:
            if k == kunci:
                return v
        return None

    def ada(self, kunci: str) -> bool:
        return self.get(kunci) is not None


# ══════════════════════════════════════════════════════
# FUNGSI REKURSIF
# ══════════════════════════════════════════════════════

def hitung_cagr(nilai_awal, nilai_akhir, n_tahun):
    """
    Hitung Compound Annual Growth Rate secara rekursif.
    CAGR = (nilai_akhir / nilai_awal) ^ (1/n) - 1

    Rekursi: setiap langkah mengurangi n_tahun hingga 1.
    """
    if nilai_awal <= 0 or nilai_akhir <= 0 or n_tahun <= 0:
        return 0.0
    if n_tahun == 1:
        return (nilai_akhir / nilai_awal) - 1.0
    # bagi menjadi setengah periode (divide and conquer)
    tengah = nilai_awal * ((nilai_akhir / nilai_awal) ** (1.0 / n_tahun))
    return hitung_cagr(tengah, nilai_akhir, n_tahun - 1)


def hitung_pertumbuhan_rekursif(data_list, index=0, hasil=None):
    """
    Hitung persentase pertumbuhan year-over-year secara rekursif.
    data_list : list nilai per tahun
    Return    : list persentase pertumbuhan
    """
    if hasil is None:
        hasil = []
    if index >= len(data_list):
        return hasil
    if index == 0:
        hasil.append(0.0)
    else:
        lalu = data_list[index - 1]
        kini = data_list[index]
        pct  = ((kini - lalu) / abs(lalu)) if lalu != 0 else 0.0
        hasil.append(pct)
    return hitung_pertumbuhan_rekursif(data_list, index + 1, hasil)


def rata_rata_rekursif(data_list, index=0, total=0.0):
    """Hitung rata-rata list secara rekursif."""
    if not data_list:
        return 0.0
    if index == len(data_list):
        return total / len(data_list)
    return rata_rata_rekursif(data_list, index + 1, total + data_list[index])


# ══════════════════════════════════════════════════════
# HELPER SAFE DIVISION
# ══════════════════════════════════════════════════════

def _div(pembilang, penyebut, default=0.0):
    """Pembagian aman — kembalikan default jika penyebut 0."""
    if penyebut == 0:
        return default
    return pembilang / penyebut


# ══════════════════════════════════════════════════════
# KELAS UTAMA
# ══════════════════════════════════════════════════════

class RatioEngine:
    """
    Menghitung semua rasio keuangan dari CompanyData
    dan menyimpannya dalam berbagai struktur data.

    Contoh:
        engine = RatioEngine(data)
        engine.hitung_semua()

        # akses hasil
        rasio_2024 = engine.rasio_per_tahun.cari_tahun(2024)
        engine.simpan_hasil()
    """

    def __init__(self, data: CompanyData):
        self.data    = data
        self.ticker  = data.profil.ticker

        # struktur data
        self.rasio_per_tahun   = SingleLinkedList()     # rasio per tahun (SLL)
        self.navigasi          = DoubleLinkedList()     # navigasi maju-mundur (DLL)
        self.rotasi            = CircularLinkedList()   # rotasi periode (CLL)
        self.riwayat           = Stack()                # riwayat operasi
        self.antrian_laporan   = Queue()                # antrian cetak
        self.lookup            = HashTable()            # lookup O(1)
        self.pohon_kategori    = buat_pohon_rasio()     # tree hierarki

        # hasil agregat
        self.semua_rasio: list[dict]  = []   # list of dict per tahun
        self.kategori_unik: set       = set()
        self.ringkasan: dict          = {}

    # ──────────────────────────────────────────────────
    # HITUNG SEMUA RASIO
    # ──────────────────────────────────────────────────

    def hitung_semua(self):
        """
        Titik masuk utama.
        Hitung rasio untuk setiap tahun, isi semua struktur data.
        """
        print(f"\n  Menghitung rasio — {self.ticker}...")

        for i in range(len(self.data.neraca)):
            b  = self.data.neraca[i]
            lr = self.data.laba_rugi[i]  if i < len(self.data.laba_rugi)  else None
            cf = self.data.arus_kas[i]   if i < len(self.data.arus_kas)    else None
            mp = self.data.data_pasar[i] if i < len(self.data.data_pasar)  else None

            rasio = self._hitung_per_tahun(b, lr, cf, mp)

            tahun = b.tahun

            # isi semua struktur data
            self.rasio_per_tahun.tambah(tahun, rasio)
            self.navigasi.tambah(tahun, rasio)
            self.rotasi.tambah(tahun, rasio)
            self.semua_rasio.append({"tahun": tahun, **rasio})

            # isi hash table
            for nama, nilai in rasio.items():
                kunci = f"{self.ticker}_{tahun}_{nama}"
                self.lookup.set(kunci, nilai)

            # catat ke stack
            self.riwayat.push(f"hitung_rasio:{tahun}")

            # daftarkan ke antrian laporan
            self.antrian_laporan.enqueue(tahun)

        # hitung ringkasan (rata-rata, tren, CAGR)
        self._hitung_ringkasan()

        # kumpulkan kategori unik (set)
        for child in self.pohon_kategori.children:
            self.kategori_unik.add(child.nama)

        print(f"  Selesai — {len(self.semua_rasio)} tahun dihitung.")
        return self

    def _hitung_per_tahun(self, b, lr, cf, mp):
        """Hitung semua rasio untuk satu tahun."""
        rasio = {}

        # ── LIKUIDITAS ────────────────────────────────
        rasio["current_ratio"] = _div(
            b.total_aset_lancar, b.total_liabilitas_lancar
        )
        rasio["quick_ratio"] = _div(
            b.total_aset_lancar - b.persediaan, b.total_liabilitas_lancar
        )
        rasio["cash_ratio"] = _div(
            b.kas_setara_kas, b.total_liabilitas_lancar
        )
        rasio["days_cash_on_hand"] = _div(
            b.kas_setara_kas * 365,
            lr.beban_operasional if lr else 1
        )

        # ── PROFITABILITAS ────────────────────────────
        if lr:
            rasio["gross_margin"]   = lr.gross_margin()
            rasio["net_margin"]     = lr.net_margin()
            rasio["ebitda_margin"]  = lr.ebitda_margin()
            rasio["roe"]            = _div(lr.laba_bersih, b.total_ekuitas)
            rasio["roa"]            = _div(lr.laba_bersih, b.total_aset)
            invested_capital        = b.total_ekuitas + b.utang_jangka_panjang
            nopat                   = lr.ebit * (1 - lr.tax_rate())
            rasio["roic"]           = _div(nopat, invested_capital)
        else:
            for k in ["gross_margin","net_margin","ebitda_margin","roe","roa","roic"]:
                rasio[k] = 0.0

        # ── SOLVABILITAS ──────────────────────────────
        rasio["der"] = _div(b.total_liabilitas, b.total_ekuitas)
        rasio["dar"] = _div(b.total_liabilitas, b.total_aset)
        rasio["interest_coverage"] = _div(
            lr.ebit if lr else 0, lr.beban_bunga if lr else 1
        )
        ebitda    = lr.ebitda if lr else 0
        net_debt  = b.net_debt()
        rasio["net_debt_ebitda"] = _div(net_debt, ebitda)

        # ── AKTIVITAS ─────────────────────────────────
        rasio["asset_turnover"] = _div(
            lr.pendapatan if lr else 0, b.total_aset
        )
        rasio["inventory_turnover"] = _div(
            lr.harga_pokok_penjualan if lr else 0, b.persediaan
        )
        rasio["receivable_days"] = _div(
            b.piutang_usaha * 365, lr.pendapatan if lr else 1
        )
        rasio["payable_days"] = _div(
            b.utang_usaha * 365, lr.harga_pokok_penjualan if lr else 1
        )

        # ── RASIO PASAR ───────────────────────────────
        harga = self.data.profil.harga_pasar
        if mp and mp.harga_saham > 0:
            harga = mp.harga_saham

        eps = lr.eps if lr else 0
        bvs = b.book_value_per_saham()

        rasio["pe_ratio"]      = _div(harga, eps)
        rasio["pb_ratio"]      = _div(harga, bvs)
        rasio["dividend_yield"] = _div(lr.dps if lr else 0, harga)

        ev     = mp.enterprise_value if mp and mp.enterprise_value > 0 else 0
        ebitda = lr.ebitda if lr else 0
        rasio["ev_ebitda"] = _div(ev, ebitda)

        # PEG Ratio — pertumbuhan EPS dihitung dari data historis
        eps_list = self.data.eps_historis()
        if len(eps_list) >= 2 and eps_list[0] > 0:
            n     = len(eps_list) - 1
            g     = hitung_cagr(eps_list[0], eps_list[-1], n) * 100
            rasio["peg_ratio"] = _div(rasio["pe_ratio"], g)
        else:
            rasio["peg_ratio"] = 0.0

        # ── FREE CASH FLOW (disimpan sebagai rasio juga) ──
        if cf:
            rasio["free_cash_flow"]   = cf.free_cash_flow()
            rasio["fcf_margin"]       = _div(cf.free_cash_flow(),
                                             lr.pendapatan if lr else 1)
            rasio["capex_to_cfo"]     = cf.capex_to_cfo()

        return rasio

    # ──────────────────────────────────────────────────
    # RINGKASAN — RATA-RATA, TREN, CAGR
    # ──────────────────────────────────────────────────

    def _hitung_ringkasan(self):
        """Hitung rata-rata, CAGR, dan tren untuk rasio utama."""
        rasio_utama = [
            "current_ratio", "der", "roe", "net_margin",
            "interest_coverage", "asset_turnover", "pe_ratio",
            "free_cash_flow", "eps_growth",
        ]

        for nama in rasio_utama:
            nilai_list = [
                d.get(nama, 0) for d in self.semua_rasio
                if d.get(nama, 0) != 0
            ]
            if not nilai_list:
                continue
            self.ringkasan[nama] = {
                "rata_rata": rata_rata_rekursif(nilai_list),
                "tren":      hitung_pertumbuhan_rekursif(nilai_list),
                "tertinggi": max(nilai_list),
                "terendah":  min(nilai_list),
            }

        # CAGR pendapatan
        pendapatan = self.data.pendapatan_historis()
        if len(pendapatan) >= 2 and pendapatan[0] > 0:
            self.ringkasan["cagr_pendapatan"] = hitung_cagr(
                pendapatan[0], pendapatan[-1], len(pendapatan) - 1
            )

        # CAGR laba bersih
        laba = [lr.laba_bersih for lr in self.data.laba_rugi]
        if len(laba) >= 2 and laba[0] > 0:
            self.ringkasan["cagr_laba"] = hitung_cagr(
                laba[0], laba[-1], len(laba) - 1
            )

        # CAGR FCF
        fcf = self.data.fcf_historis()
        if len(fcf) >= 2 and fcf[0] > 0:
            self.ringkasan["cagr_fcf"] = hitung_cagr(
                fcf[0], fcf[-1], len(fcf) - 1
            )

    # ──────────────────────────────────────────────────
    # SEARCHING
    # ──────────────────────────────────────────────────

    def cari_rasio(self, nama_rasio, tahun=None):
        """
        Cari nilai rasio tertentu.
        Jika tahun diisi → cari tahun spesifik (via Hash Table O(1)).
        Jika tidak → kembalikan semua tahun.
        """
        if tahun:
            kunci = f"{self.ticker}_{tahun}_{nama_rasio}"
            nilai = self.lookup.get(kunci)
            return {tahun: nilai} if nilai is not None else {}

        # cari di semua tahun via SLL
        hasil = {}
        node  = self.rasio_per_tahun.head
        while node:
            if nama_rasio in node.rasio:
                hasil[node.tahun] = node.rasio[nama_rasio]
            node = node.next
        return hasil

    def cari_tahun_terbaik(self, nama_rasio, tertinggi=True):
        """
        Cari tahun dengan nilai rasio tertinggi atau terendah.
        Menggunakan searching linear pada SLL.
        """
        best_tahun = None
        best_nilai = None
        node       = self.rasio_per_tahun.head

        while node:
            nilai = node.rasio.get(nama_rasio)
            if nilai is not None:
                if best_nilai is None:
                    best_tahun = node.tahun
                    best_nilai = nilai
                elif tertinggi and nilai > best_nilai:
                    best_tahun = node.tahun
                    best_nilai = nilai
                elif not tertinggi and nilai < best_nilai:
                    best_tahun = node.tahun
                    best_nilai = nilai
            node = node.next

        return best_tahun, best_nilai

    # ──────────────────────────────────────────────────
    # SORTING
    # ──────────────────────────────────────────────────

    def urutkan_rasio(self, nama_rasio, ascending=True):
        """
        Sorting — urutkan tahun berdasarkan nilai rasio tertentu.
        Return: list of tuple (tahun, nilai) terurut.
        """
        data = [
            (d["tahun"], d.get(nama_rasio, 0))
            for d in self.semua_rasio
            if d.get(nama_rasio) is not None
        ]
        data = merge_sort(data, key=lambda x: x[1], reverse=not ascending)
        return data

    def ranking_rasio(self, nama_rasio):
        """
        Buat ranking semua tahun berdasarkan nilai rasio.
        Return: list of tuple (rank, tahun, nilai)
        """
        terurut = self.urutkan_rasio(nama_rasio, ascending=False)
        return [(i + 1, tahun, nilai) for i, (tahun, nilai) in enumerate(terurut)]

    # ──────────────────────────────────────────────────
    # FILE HANDLER — simpan hasil ke file
    # ──────────────────────────────────────────────────

    def simpan_hasil(self, format_file="txt"):
        """
        Simpan hasil rasio ke file di folder outputs/.
        Format: 'txt' atau 'json'
        """
        tanggal   = datetime.today().strftime(cfg.OUTPUT_DATE_FORMAT)
        nama_file = f"{self.ticker}_rasio_{tanggal}.{format_file}"
        path      = cfg.OUTPUTS_DIR / nama_file

        if format_file == "json":
            self._simpan_json(path)
        else:
            self._simpan_txt(path)

        print(f"  Hasil disimpan: {path}")
        self.riwayat.push(f"simpan:{path}")
        return path

    def _simpan_txt(self, path):
        """Tulis hasil rasio ke file teks."""
        with open(path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write(f"LAPORAN RASIO KEUANGAN\n")
            f.write(f"{self.data.profil.nama} ({self.ticker})\n")
            f.write(f"Tanggal : {datetime.today().strftime('%d %b %Y')}\n")
            f.write("=" * 60 + "\n\n")

            # tulis rasio per tahun dari antrian
            sementara = Queue()
            while not self.antrian_laporan.kosong():
                tahun = self.antrian_laporan.dequeue()
                sementara.enqueue(tahun)
                node  = self.rasio_per_tahun.cari_tahun(tahun)
                if not node:
                    continue
                f.write(f"  TAHUN {tahun}\n")
                f.write("  " + "-" * 40 + "\n")

                # kelompokkan rasio per kategori (gunakan tree)
                for cat_node in self.pohon_kategori.children:
                    f.write(f"  [{cat_node.nama}]\n")
                    for nama_rasio in cat_node.rasio:
                        nilai = node.rasio.get(nama_rasio)
                        if nilai is None:
                            continue
                        meta  = cfg.RATIO_META.get(nama_rasio, {})
                        label = meta.get("name", nama_rasio)
                        unit  = meta.get("unit", "")
                        if unit == "%":
                            f.write(f"    {label:<28}: {nilai*100:>8.2f} %\n")
                        else:
                            f.write(f"    {label:<28}: {nilai:>10.2f} {unit}\n")
                f.write("\n")

            # kembalikan antrian
            while not sementara.kosong():
                self.antrian_laporan.enqueue(sementara.dequeue())

            # tulis ringkasan CAGR
            f.write("=" * 60 + "\n")
            f.write("  RINGKASAN\n")
            f.write("=" * 60 + "\n")
            if "cagr_pendapatan" in self.ringkasan:
                f.write(f"  CAGR Pendapatan : {self.ringkasan['cagr_pendapatan']*100:.2f}%\n")
            if "cagr_laba" in self.ringkasan:
                f.write(f"  CAGR Laba Bersih: {self.ringkasan['cagr_laba']*100:.2f}%\n")
            if "cagr_fcf" in self.ringkasan:
                f.write(f"  CAGR FCF        : {self.ringkasan['cagr_fcf']*100:.2f}%\n")

    def _simpan_json(self, path):
        """Tulis hasil rasio ke file JSON."""
        output = {
            "ticker":    self.ticker,
            "nama":      self.data.profil.nama,
            "tanggal":   datetime.today().strftime(cfg.OUTPUT_DATE_FORMAT),
            "rasio":     self.semua_rasio,
            "ringkasan": {
                k: (v if not isinstance(v, dict) else {
                    "rata_rata":  v.get("rata_rata", 0),
                    "tertinggi":  v.get("tertinggi", 0),
                    "terendah":   v.get("terendah", 0),
                })
                for k, v in self.ringkasan.items()
            },
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

    def baca_hasil(self, path):
        """
        File Handler — baca hasil yang sudah disimpan.
        Return: dict hasil atau None jika gagal.
        """
        path = Path(path)
        if not path.exists():
            print(f"  ERROR: File tidak ditemukan — {path}")
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"  ERROR membaca file: {e}")
            return None

    # ──────────────────────────────────────────────────
    # TAMPILKAN HASIL DI TERMINAL
    # ──────────────────────────────────────────────────

    def tampilkan(self, n_tahun=None):
        """
        Cetak tabel rasio ke terminal.
        n_tahun: tampilkan n tahun terakhir saja (pakai Circular LL)
        """
        if n_tahun:
            window = self.rotasi.window(n_tahun)
            data   = window
        else:
            data = [(node.tahun, node.rasio)
                    for node in self.rasio_per_tahun.ke_list()]

        print()
        print("=" * 60)
        print(f"  RASIO KEUANGAN — {self.data.profil.nama} ({self.ticker})")
        print("=" * 60)

        for cat_node in self.pohon_kategori.children:
            print(f"\n  [{cat_node.nama}]")
            print(f"  {'Rasio':<28}", end="")
            for tahun, _ in data:
                print(f"  {tahun:>8}", end="")
            print()
            print("  " + "-" * (28 + len(data) * 10))

            for nama_rasio in cat_node.rasio:
                meta  = cfg.RATIO_META.get(nama_rasio, {})
                label = meta.get("name", nama_rasio)
                unit  = meta.get("unit", "")
                print(f"  {label:<28}", end="")
                for _, rasio in data:
                    nilai = rasio.get(nama_rasio, 0)
                    if unit == "%":
                        print(f"  {nilai*100:>7.1f}%", end="")
                    elif unit in ("x", "hari"):
                        print(f"  {nilai:>7.2f}{unit}", end="")
                    else:
                        print(f"  {nilai:>8.2f}", end="")
                print()

        # Ringkasan CAGR
        print()
        print("=" * 60)
        print("  CAGR")
        print("=" * 60)
        cagr_items = [
            ("cagr_pendapatan", "Pendapatan"),
            ("cagr_laba",       "Laba Bersih"),
            ("cagr_fcf",        "Free Cash Flow"),
        ]
        for kunci, label in cagr_items:
            if kunci in self.ringkasan:
                print(f"  {label:<20}: {self.ringkasan[kunci]*100:.2f}%")
        print()
        