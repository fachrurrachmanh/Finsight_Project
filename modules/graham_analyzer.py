"""
modules/graham_analyzer.py
===========================
Analisis value investing metode Benjamin Graham.

Mencakup:
  - Graham Number & Margin of Safety
  - 7 Kriteria Defensive Investor
  - NCAV / Cigar Butt Test
  - Earnings Power Value (EPV)
  - DCF Konservatif
  - Graham Scorecard

Struktur data (rubrik):
  - Single Linked List   : rantai hasil analisis per tahun
  - Double Linked List   : perbandingan kriteria tahun ini vs lalu
  - Circular Linked List : rotasi window periode Graham
  - Stack                : riwayat kalkulasi
  - Queue                : antrian kriteria yang diproses
  - Hash Table           : lookup hasil per kriteria O(1)
  - Tree                 : hierarki komponen scorecard
  - List/Tuple/Set/Dict  : wadah hasil
  - Sorting              : ranking kriteria dan MoS
  - Searching            : cari kriteria dan tahun terbaik
  - Rekursif             : DCF, EPV bertingkat
  - File Handler         : simpan hasil ke file
  - OOP                  : class GrahamAnalyzer
"""

import sys
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config as cfg
from models.company import CompanyData


# ══════════════════════════════════════════════════════
# HELPER
# ══════════════════════════════════════════════════════

def _div(a, b, default=0.0):
    return a / b if b != 0 else default

def _safe_sqrt(nilai):
    return nilai ** 0.5 if nilai > 0 else 0.0


# ══════════════════════════════════════════════════════
# SINGLE LINKED LIST — rantai hasil per tahun
# ══════════════════════════════════════════════════════

class GrahamNode:
    def __init__(self, tahun, hasil: dict):
        self.tahun = tahun
        self.hasil = hasil   # { nama_metrik: nilai }
        self.next  = None


class SingleLinkedList:
    def __init__(self):
        self.head = None

    def tambah(self, tahun, hasil: dict):
        node = GrahamNode(tahun, hasil)
        if self.head is None:
            self.head = node
            return
        cur = self.head
        while cur.next:
            cur = cur.next
        cur.next = node

    def cari(self, tahun):
        cur = self.head
        while cur:
            if cur.tahun == tahun:
                return cur
            cur = cur.next
        return None

    def ke_list(self):
        hasil, cur = [], self.head
        while cur:
            hasil.append(cur)
            cur = cur.next
        return hasil


# ══════════════════════════════════════════════════════
# DOUBLE LINKED LIST — bandingkan kriteria antar tahun
# ══════════════════════════════════════════════════════

class DoubleNode:
    def __init__(self, tahun, hasil: dict):
        self.tahun = tahun
        self.hasil = hasil
        self.next  = None
        self.prev  = None


class DoubleLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def tambah(self, tahun, hasil: dict):
        node = DoubleNode(tahun, hasil)
        if self.head is None:
            self.head = self.tail = node
            return
        node.prev      = self.tail
        self.tail.next = node
        self.tail       = node

    def terbaru(self):
        return self.tail

    def perubahan(self, kunci):
        """
        Bandingkan nilai kunci dari tahun ke tahun.
        Return list (tahun, nilai, naik/turun/tetap)
        """
        hasil, cur = [], self.head
        while cur:
            nilai = cur.hasil.get(kunci, 0)
            if cur.prev:
                lalu = cur.prev.hasil.get(kunci, 0)
                if nilai > lalu:
                    arah = "naik"
                elif nilai < lalu:
                    arah = "turun"
                else:
                    arah = "tetap"
            else:
                arah = "-"
            hasil.append((cur.tahun, nilai, arah))
            cur = cur.next
        return hasil


# ══════════════════════════════════════════════════════
# CIRCULAR LINKED LIST — rotasi window periode
# ══════════════════════════════════════════════════════

class CircularNode:
    def __init__(self, tahun, hasil: dict):
        self.tahun = tahun
        self.hasil = hasil
        self.next  = None


class CircularLinkedList:
    def __init__(self):
        self.head   = None
        self.ukuran = 0

    def tambah(self, tahun, hasil: dict):
        node = CircularNode(tahun, hasil)
        if self.head is None:
            self.head = node
            node.next = self.head
        else:
            cur = self.head
            while cur.next != self.head:
                cur = cur.next
            cur.next  = node
            node.next = self.head
        self.ukuran += 1

    def window(self, n):
        if not self.head or n <= 0:
            return []
        hasil, cur = [], self.head
        for _ in range(max(0, self.ukuran - n)):
            cur = cur.next
        for _ in range(min(n, self.ukuran)):
            hasil.append((cur.tahun, cur.hasil))
            cur = cur.next
        return hasil


# ══════════════════════════════════════════════════════
# STACK — riwayat kalkulasi
# ══════════════════════════════════════════════════════

class Stack:
    def __init__(self):
        self._data = []

    def push(self, item):   self._data.append(item)
    def pop(self):          return self._data.pop() if self._data else None
    def peek(self):         return self._data[-1] if self._data else None
    def kosong(self):       return len(self._data) == 0
    def ukuran(self):       return len(self._data)


# ══════════════════════════════════════════════════════
# QUEUE — antrian kriteria yang diproses
# ══════════════════════════════════════════════════════

class Queue:
    def __init__(self):
        self._data = []

    def enqueue(self, item):  self._data.append(item)
    def dequeue(self):        return self._data.pop(0) if self._data else None
    def kosong(self):         return len(self._data) == 0
    def ukuran(self):         return len(self._data)
    def semua(self):          return list(self._data)


# ══════════════════════════════════════════════════════
# HASH TABLE — lookup hasil kriteria O(1)
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
# TREE — hierarki komponen scorecard Graham
# ══════════════════════════════════════════════════════

class TreeNode:
    def __init__(self, nama, bobot=0.0):
        self.nama     = nama
        self.bobot    = bobot    # bobot dalam scorecard (0.0–1.0)
        self.children = []
        self.komponen = []       # daftar sub-komponen

    def tambah_child(self, child):
        self.children.append(child)
        return child

    def tambah_komponen(self, nama, bobot=0.0):
        self.komponen.append((nama, bobot))


def buat_pohon_scorecard():
    """
    Pohon hierarki Graham Scorecard.

    Graham Scorecard
    ├── Graham Number & MoS      (bobot 25%)
    │   ├── graham_number
    │   ├── margin_of_safety
    │   └── rekomendasi
    ├── 7 Kriteria Defensive     (bobot 20%)
    │   ├── kriteria_1 s/d 7
    ├── NCAV Test                (bobot 10%)
    │   ├── ncav_per_saham
    │   └── ncav_discount
    ├── Earnings Quality         (bobot 15%)
    │   ├── konsistensi_laba
    │   ├── accrual_ratio
    │   └── eps_growth
    ├── Balance Sheet Strength   (bobot 15%)
    │   ├── working_capital
    │   ├── tangible_bv
    │   └── net_debt_ratio
    ├── Dividend Consistency     (bobot 10%)
    │   ├── tahun_dividen
    │   └── payout_ratio
    └── Risk Penalty             (bobot 5%)
        └── risk_score
    """
    root = TreeNode("Graham Scorecard", bobot=1.0)

    mos = root.tambah_child(TreeNode("Graham Number & MoS", bobot=0.25))
    mos.tambah_komponen("graham_number",    0.40)
    mos.tambah_komponen("margin_of_safety", 0.40)
    mos.tambah_komponen("rekomendasi",      0.20)

    k7 = root.tambah_child(TreeNode("7 Kriteria Defensive", bobot=0.20))
    for i in range(1, 8):
        k7.tambah_komponen(f"kriteria_{i}", round(1/7, 4))

    ncav = root.tambah_child(TreeNode("NCAV Test", bobot=0.10))
    ncav.tambah_komponen("ncav_per_saham", 0.50)
    ncav.tambah_komponen("ncav_discount",  0.50)

    eq = root.tambah_child(TreeNode("Earnings Quality", bobot=0.15))
    eq.tambah_komponen("konsistensi_laba", 0.40)
    eq.tambah_komponen("accrual_ratio",    0.30)
    eq.tambah_komponen("eps_growth",       0.30)

    bs = root.tambah_child(TreeNode("Balance Sheet Strength", bobot=0.15))
    bs.tambah_komponen("working_capital", 0.40)
    bs.tambah_komponen("tangible_bv",     0.30)
    bs.tambah_komponen("net_debt_ratio",  0.30)

    div = root.tambah_child(TreeNode("Dividend Consistency", bobot=0.10))
    div.tambah_komponen("tahun_dividen", 0.60)
    div.tambah_komponen("payout_ratio",  0.40)

    risk = root.tambah_child(TreeNode("Risk Penalty", bobot=0.05))
    risk.tambah_komponen("risk_score", 1.00)

    return root


def tampilkan_pohon(node, indent=0):
    """Tampilkan pohon secara rekursif."""
    prefix = "  " * indent
    bobot_str = f" [{node.bobot*100:.0f}%]" if node.bobot > 0 else ""
    print(f"{prefix}{node.nama}{bobot_str}")
    for nama, bobot in node.komponen:
        print(f"{prefix}  · {nama} ({bobot*100:.0f}%)")
    for child in node.children:
        tampilkan_pohon(child, indent + 1)


def cari_bobot_komponen(root, nama_komponen):
    """Searching di tree — cari bobot komponen tertentu."""
    for child in root.children:
        for nama, bobot in child.komponen:
            if nama == nama_komponen:
                return child.bobot * bobot
        for subchild in child.children:
            for nama, bobot in subchild.komponen:
                if nama == nama_komponen:
                    return child.bobot * subchild.bobot * bobot
    return 0.0


# ══════════════════════════════════════════════════════
# REKURSIF — DCF & EPV
# ══════════════════════════════════════════════════════

def dcf_rekursif(fcf, wacc, growth, tahun_tersisa, terminal_growth=0.03):
    """
    Hitung present value FCF secara rekursif.
    Setiap panggilan mendiskon satu tahun ke depan.

    fcf           : FCF tahun ini
    wacc          : discount rate
    growth        : growth rate FCF
    tahun_tersisa : sisa tahun proyeksi
    terminal_growth: pertumbuhan jangka panjang (terminal value)
    """
    if tahun_tersisa == 0:
        # Terminal value: FCF tahun terakhir / (wacc - terminal_growth)
        fcf_terminal = fcf * (1 + terminal_growth)
        return _div(fcf_terminal, wacc - terminal_growth)

    fcf_depan = fcf * (1 + growth)
    pv_depan  = _div(fcf_depan, 1 + wacc)

    return pv_depan + _div(
        dcf_rekursif(fcf_depan, wacc, growth * 0.9,
                     tahun_tersisa - 1, terminal_growth),
        1 + wacc
    )


def epv_rekursif(ebit_list, tax_rate, wacc, index=0, total=0.0):
    """
    Hitung Earnings Power Value secara rekursif.
    EPV = rata-rata NOPAT historis / WACC
    NOPAT = EBIT * (1 - tax_rate)
    """
    if index == len(ebit_list):
        rata_nopat = _div(total, len(ebit_list))
        return _div(rata_nopat, wacc)
    nopat = ebit_list[index] * (1 - tax_rate)
    return epv_rekursif(ebit_list, tax_rate, wacc, index + 1, total + nopat)


def hitung_cagr_rekursif(awal, akhir, n):
    """CAGR dihitung rekursif dengan divide and conquer."""
    if awal <= 0 or akhir <= 0 or n <= 0:
        return 0.0
    if n == 1:
        return (akhir / awal) - 1.0
    tengah = awal * ((akhir / awal) ** (1.0 / n))
    return hitung_cagr_rekursif(tengah, akhir, n - 1)


def count_laba_positif(laba_list, index=0, count=0):
    """Hitung jumlah tahun laba positif secara rekursif."""
    if index == len(laba_list):
        return count
    tambah = 1 if laba_list[index] > 0 else 0
    return count_laba_positif(laba_list, index + 1, count + tambah)


def count_dividen_positif(dps_list, index=0, count=0):
    """Hitung jumlah tahun yang membayar dividen secara rekursif."""
    if index == len(dps_list):
        return count
    tambah = 1 if dps_list[index] > 0 else 0
    return count_dividen_positif(dps_list, index + 1, count + tambah)


def rata_rata_rekursif(data, index=0, total=0.0):
    if not data:
        return 0.0
    if index == len(data):
        return total / len(data)
    return rata_rata_rekursif(data, index + 1, total + data[index])


# ══════════════════════════════════════════════════════
# KELAS UTAMA
# ══════════════════════════════════════════════════════

class GrahamAnalyzer:
    """
    Analisis fundamental metode Benjamin Graham.

    Contoh:
        analyzer = GrahamAnalyzer(data)
        hasil    = analyzer.analisis()
        analyzer.tampilkan()
        analyzer.simpan()
    """

    def __init__(self, data: CompanyData,
                 wacc=0.10, growth_rate=0.05, tahun_proyeksi=5):
        self.data           = data
        self.ticker         = data.profil.ticker
        self.wacc           = wacc
        self.growth_rate    = growth_rate
        self.tahun_proyeksi = tahun_proyeksi

        # struktur data
        self.rantai         = SingleLinkedList()
        self.navigasi       = DoubleLinkedList()
        self.rotasi         = CircularLinkedList()
        self.riwayat        = Stack()
        self.antrian        = Queue()
        self.lookup         = HashTable()
        self.pohon          = buat_pohon_scorecard()

        # hasil
        self.hasil_per_tahun: list[dict] = []
        self.scorecard:       dict       = {}
        self.valuasi:         dict       = {}
        self.kriteria_lulus:  set        = set()
        self.kriteria_gagal:  set        = set()

    # ──────────────────────────────────────────────────
    # TITIK MASUK
    # ──────────────────────────────────────────────────

    def analisis(self):
        """Jalankan seluruh analisis Graham."""
        print(f"\n  Analisis Graham — {self.ticker}...")

        b  = self.data.neraca_terbaru()
        lr = self.data.laba_rugi_terbaru()
        cf = self.data.arus_kas_terbaru()

        if not b or not lr:
            print("  ERROR: Data tidak cukup.")
            return self

        harga = self.data.profil.harga_pasar

        # ── antrian komponen analisis ─────────────────
        self.antrian.enqueue("graham_number")
        self.antrian.enqueue("valuasi_multi")
        self.antrian.enqueue("7_kriteria")
        self.antrian.enqueue("ncav")
        self.antrian.enqueue("earnings_quality")
        self.antrian.enqueue("balance_sheet")
        self.antrian.enqueue("dividend")
        self.antrian.enqueue("scorecard")

        # proses antrian satu per satu
        while not self.antrian.kosong():
            komponen = self.antrian.dequeue()
            self.riwayat.push(f"proses:{komponen}")

            if komponen == "graham_number":
                self._hitung_graham_number(b, lr, harga)
            elif komponen == "valuasi_multi":
                self._hitung_valuasi(b, lr, cf, harga)
            elif komponen == "7_kriteria":
                self._cek_7_kriteria(b, lr)
            elif komponen == "ncav":
                self._hitung_ncav(b, harga)
            elif komponen == "earnings_quality":
                self._hitung_earnings_quality(lr)
            elif komponen == "balance_sheet":
                self._hitung_balance_sheet(b, lr)
            elif komponen == "dividend":
                self._hitung_dividend()
            elif komponen == "scorecard":
                self._hitung_scorecard()

        # isi linked list per tahun
        for i, b_hist in enumerate(self.data.neraca):
            lr_hist = self.data.laba_rugi[i] if i < len(self.data.laba_rugi) else None
            if not lr_hist:
                continue
            hasil_tahun = self._hitung_per_tahun(b_hist, lr_hist, harga)
            self.rantai.tambah(b_hist.tahun, hasil_tahun)
            self.navigasi.tambah(b_hist.tahun, hasil_tahun)
            self.rotasi.tambah(b_hist.tahun, hasil_tahun)
            self.hasil_per_tahun.append({"tahun": b_hist.tahun, **hasil_tahun})

            for kunci, nilai in hasil_tahun.items():
                self.lookup.set(f"{self.ticker}_{b_hist.tahun}_{kunci}", nilai)

        print("  Selesai.")
        return self

    # ──────────────────────────────────────────────────
    # 1. GRAHAM NUMBER & MARGIN OF SAFETY
    # ──────────────────────────────────────────────────

    def _hitung_graham_number(self, b, lr, harga):
        eps = lr.eps
        bvs = b.book_value_per_saham()

        angka = _safe_sqrt(cfg.GRAHAM["graham_multiplier"] * eps * bvs)
        mos   = _div(angka - harga, angka)

        self.valuasi["graham_number"]    = angka
        self.valuasi["margin_of_safety"] = mos

        # tentukan rekomendasi
        if mos >= 0.40:
            rek = "STRONG BUY"
        elif mos >= 0.33:
            rek = "BUY"
        elif mos >= 0.20:
            rek = "ACCUMULATE"
        elif mos >= 0.10:
            rek = "WATCH"
        elif mos >= 0:
            rek = "AVOID"
        else:
            rek = "OVERVALUED"

        self.valuasi["rekomendasi_mos"] = rek
        self.riwayat.push(f"graham_number:{angka:.2f}|mos:{mos*100:.1f}%")

    # ──────────────────────────────────────────────────
    # 2. VALUASI MULTI-METODE
    # ──────────────────────────────────────────────────

    def _hitung_valuasi(self, b, lr, cf, harga):
        saham = b.jumlah_saham_beredar

        # ── EPV (rekursif) ────────────────────────────
        ebit_list = [i.ebit for i in self.data.laba_rugi]
        tax_rate  = lr.tax_rate()
        epv_total = epv_rekursif(ebit_list, tax_rate, self.wacc)
        epv_ps    = _div(epv_total, saham)

        # ── DCF (rekursif) ────────────────────────────
        fcf_kini  = cf.free_cash_flow() if cf else 0
        dcf_total = dcf_rekursif(
            fcf_kini, self.wacc,
            self.growth_rate, self.tahun_proyeksi
        )
        dcf_ps = _div(dcf_total, saham)

        # ── Nilai Intrinsik — ambil yang paling konservatif ──
        kandidat = {
            "graham_number": self.valuasi.get("graham_number", 0),
            "epv":           epv_ps,
            "dcf":           dcf_ps,
        }
        # filter nilai > 0
        kandidat_valid = {k: v for k, v in kandidat.items() if v > 0}

        if kandidat_valid:
            nilai_intrinsik = min(kandidat_valid.values())   # paling konservatif
        else:
            nilai_intrinsik = 0.0

        mos_final = _div(nilai_intrinsik - harga, nilai_intrinsik)

        self.valuasi.update({
            "epv_per_saham":  epv_ps,
            "dcf_per_saham":  dcf_ps,
            "nilai_intrinsik_konservatif": nilai_intrinsik,
            "margin_of_safety_final":      mos_final,
            "wacc_digunakan":  self.wacc,
            "growth_digunakan": self.growth_rate,
        })

        self.riwayat.push(f"valuasi_multi:epv={epv_ps:.0f}|dcf={dcf_ps:.0f}")

    # ──────────────────────────────────────────────────
    # 3. 7 KRITERIA DEFENSIVE INVESTOR GRAHAM
    # ──────────────────────────────────────────────────

    def _cek_7_kriteria(self, b, lr):
        """
        Graham Defensive Investor — 7 kriteria:
        1. Ukuran perusahaan memadai
        2. Kondisi keuangan kuat (Current Ratio >= 2.0)
        3. Stabilitas laba (tidak rugi >= min_years_data tahun)
        4. Rekam dividen (bayar dividen konsisten)
        5. Pertumbuhan laba (EPS naik >= 33% dalam periode data)
        6. P/E <= 15x
        7. P/BV <= 1.5x
        """
        harga = self.data.profil.harga_pasar
        hasil = {}

        # Kriteria 1 — ukuran perusahaan
        # threshold: total aset minimal 1 triliun (1_000_000 juta)
        hasil["kriteria_1"] = b.total_aset >= 1_000_000

        # Kriteria 2 — kondisi keuangan
        current_ratio = _div(b.total_aset_lancar, b.total_liabilitas_lancar)
        hasil["kriteria_2"] = current_ratio >= cfg.GRAHAM["min_current_ratio"]

        # Kriteria 3 — stabilitas laba (rekursif)
        laba_list = [i.laba_bersih for i in self.data.laba_rugi]
        n_positif = count_laba_positif(laba_list)
        hasil["kriteria_3"] = n_positif == len(laba_list)

        # Kriteria 4 — rekam dividen (rekursif)
        dps_list  = self.data.dps_historis()
        n_dividen = count_dividen_positif(dps_list)
        hasil["kriteria_4"] = n_dividen >= cfg.GRAHAM["min_years_data"]

        # Kriteria 5 — pertumbuhan EPS
        eps_list = self.data.eps_historis()
        if len(eps_list) >= 2 and eps_list[0] > 0:
            cagr_eps = hitung_cagr_rekursif(eps_list[0], eps_list[-1], len(eps_list) - 1)
            growth_total = (eps_list[-1] - eps_list[0]) / eps_list[0]
            hasil["kriteria_5"] = growth_total >= cfg.GRAHAM["min_eps_growth_10yr"]
        else:
            hasil["kriteria_5"] = False

        # Kriteria 6 — P/E <= 15x
        pe = _div(harga, lr.eps)
        hasil["kriteria_6"] = 0 < pe <= cfg.GRAHAM["max_pe_ratio"]

        # Kriteria 7 — P/BV <= 1.5x
        bvs = b.book_value_per_saham()
        pb  = _div(harga, bvs)
        hasil["kriteria_7"] = 0 < pb <= cfg.GRAHAM["max_pb_ratio"]

        # hitung skor
        skor  = sum(1 for v in hasil.values() if v)
        total = len(hasil)

        self.scorecard["kriteria_7"]       = hasil
        self.scorecard["skor_kriteria_7"]  = skor
        self.scorecard["total_kriteria_7"] = total

        # isi set lulus / gagal
        for nama, lulus in hasil.items():
            if lulus:
                self.kriteria_lulus.add(nama)
            else:
                self.kriteria_gagal.add(nama)

        # isi hash table
        for nama, lulus in hasil.items():
            self.lookup.set(f"{self.ticker}_kriteria_{nama}", lulus)

        self.riwayat.push(f"7_kriteria:{skor}/{total}")

    # ──────────────────────────────────────────────────
    # 4. NCAV / CIGAR BUTT TEST
    # ──────────────────────────────────────────────────

    def _hitung_ncav(self, b, harga):
        ncav_ps  = b.ncav_per_saham()
        nnwc_ps  = _div(b.nnwc(), b.jumlah_saham_beredar)
        discount = _div(harga, ncav_ps) if ncav_ps > 0 else 999

        if ncav_ps > 0 and harga < ncav_ps * cfg.GRAHAM["ncav_discount"]:
            status = "CIGAR BUTT — beli"
        elif ncav_ps > 0 and harga < ncav_ps:
            status = "MURAH — mendekati NCAV"
        else:
            status = "DI ATAS NCAV"

        self.scorecard["ncav"] = {
            "ncav_per_saham":  ncav_ps,
            "nnwc_per_saham":  nnwc_ps,
            "harga_vs_ncav":   discount,
            "status":          status,
        }
        self.riwayat.push(f"ncav:{ncav_ps:.0f}|status:{status}")

    # ──────────────────────────────────────────────────
    # 5. EARNINGS QUALITY
    # ──────────────────────────────────────────────────

    def _hitung_earnings_quality(self, lr):
        laba_list = [i.laba_bersih for i in self.data.laba_rugi]
        fcf_list  = self.data.fcf_historis()
        eps_list  = self.data.eps_historis()

        # konsistensi laba — semua tahun positif
        n_positif    = count_laba_positif(laba_list)
        konsistensi  = _div(n_positif, len(laba_list))

        # accrual ratio = (Net Income - FCF) / Total Aset (terbaru)
        b          = self.data.neraca_terbaru()
        net_income = self.data.laba_rugi_terbaru().laba_bersih
        fcf        = self.data.arus_kas_terbaru().free_cash_flow() if self.data.arus_kas else 0
        accrual    = _div(net_income - fcf, b.total_aset)

        # kualitas accrual
        if abs(accrual) < cfg.RISK["accrual_ratio_warning"]:
            kualitas_accrual = "TINGGI"
        elif abs(accrual) < cfg.RISK["accrual_ratio_danger"]:
            kualitas_accrual = "SEDANG"
        else:
            kualitas_accrual = "RENDAH"

        # pertumbuhan EPS (rekursif CAGR)
        if len(eps_list) >= 2 and eps_list[0] > 0:
            cagr_eps = hitung_cagr_rekursif(eps_list[0], eps_list[-1], len(eps_list) - 1)
        else:
            cagr_eps = 0.0

        # volatilitas EPS — standar deviasi manual
        avg_eps  = rata_rata_rekursif(eps_list)
        variance = rata_rata_rekursif([(e - avg_eps) ** 2 for e in eps_list])
        std_eps  = variance ** 0.5
        cv_eps   = _div(std_eps, avg_eps)   # Coefficient of Variation

        if cv_eps < cfg.RISK["eps_cv_stable"]:
            stabilitas_eps = "STABIL"
        elif cv_eps < cfg.RISK["eps_cv_moderate"]:
            stabilitas_eps = "MODERAT"
        else:
            stabilitas_eps = "TIDAK STABIL"

        self.scorecard["earnings_quality"] = {
            "konsistensi_laba":  konsistensi,
            "n_tahun_positif":   n_positif,
            "accrual_ratio":     accrual,
            "kualitas_accrual":  kualitas_accrual,
            "cagr_eps":          cagr_eps,
            "cv_eps":            cv_eps,
            "stabilitas_eps":    stabilitas_eps,
        }
        self.riwayat.push(f"earnings_quality:accrual={accrual:.3f}")

    # ──────────────────────────────────────────────────
    # 6. BALANCE SHEET STRENGTH
    # ──────────────────────────────────────────────────

    def _hitung_balance_sheet(self, b, lr):
        wc      = b.working_capital()
        tbv     = b.tangible_book_value()
        tbv_ps  = b.tangible_bv_per_saham()
        net_debt = b.net_debt()

        # DER check
        der     = _div(b.total_liabilitas, b.total_ekuitas)
        der_ok  = der <= cfg.GRAHAM["max_der"]

        # Long-term debt vs Net Current Assets
        nca         = b.total_aset_lancar - b.total_liabilitas_lancar
        ltd_vs_nca  = _div(b.utang_jangka_panjang, nca) if nca > 0 else 999
        ltd_ok      = b.utang_jangka_panjang <= nca

        # Interest coverage
        ic     = _div(lr.ebit, lr.beban_bunga)
        ic_ok  = ic >= cfg.RISK["min_interest_coverage"]

        self.scorecard["balance_sheet"] = {
            "working_capital":       wc,
            "tangible_book_value":   tbv,
            "tangible_bv_per_saham": tbv_ps,
            "net_debt":              net_debt,
            "der":                   der,
            "der_ok":                der_ok,
            "ltd_vs_nca":            ltd_vs_nca,
            "ltd_ok":                ltd_ok,
            "interest_coverage":     ic,
            "ic_ok":                 ic_ok,
        }
        self.riwayat.push(f"balance_sheet:der={der:.2f}|ic={ic:.2f}")

    # ──────────────────────────────────────────────────
    # 7. DIVIDEND CONSISTENCY
    # ──────────────────────────────────────────────────

    def _hitung_dividend(self):
        dps_list   = self.data.dps_historis()
        n_dividen  = count_dividen_positif(dps_list)
        lr_terbaru = self.data.laba_rugi_terbaru()

        payout = lr_terbaru.payout_ratio() if lr_terbaru else 0
        cov    = lr_terbaru.dividend_coverage() if lr_terbaru else 0

        payout_ok = cfg.GRAHAM["payout_ratio_min"] <= payout <= cfg.GRAHAM["payout_ratio_max"]
        cov_ok    = cov >= cfg.GRAHAM["min_dividend_coverage"]

        # CAGR dividen (rekursif)
        dps_valid = [d for d in dps_list if d > 0]
        if len(dps_valid) >= 2:
            cagr_dps = hitung_cagr_rekursif(dps_valid[0], dps_valid[-1], len(dps_valid) - 1)
        else:
            cagr_dps = 0.0

        self.scorecard["dividend"] = {
            "tahun_bayar_dividen":  n_dividen,
            "total_tahun_data":     len(dps_list),
            "konsisten":            n_dividen == len(dps_list),
            "payout_ratio":         payout,
            "payout_ok":            payout_ok,
            "dividend_coverage":    cov,
            "coverage_ok":          cov_ok,
            "cagr_dps":             cagr_dps,
        }
        self.riwayat.push(f"dividend:n={n_dividen}|payout={payout:.2f}")

    # ──────────────────────────────────────────────────
    # 8. GRAHAM SCORECARD
    # ──────────────────────────────────────────────────

    def _hitung_scorecard(self):
        """
        Agregasi semua komponen menjadi skor akhir 0–100.
        Bobot diambil dari cfg.SCORECARD_WEIGHTS.
        """
        skor_komponen = {}

        # ── Graham Number & MoS (25%) ──────────────────
        mos = self.valuasi.get("margin_of_safety", 0)
        if mos >= 0.40:
            s = 100
        elif mos >= 0.33:
            s = 85
        elif mos >= 0.20:
            s = 65
        elif mos >= 0:
            s = 40
        else:
            s = 10
        skor_komponen["graham_number_mos"] = s

        # ── 7 Kriteria (20%) ─────────────────────────
        skor_k7 = self.scorecard.get("skor_kriteria_7", 0)
        total_k7 = self.scorecard.get("total_kriteria_7", 7)
        skor_komponen["defensive_criteria"] = round(_div(skor_k7, total_k7) * 100)

        # ── NCAV Test (10%) ──────────────────────────
        ncav = self.scorecard.get("ncav", {})
        status_ncav = ncav.get("status", "")
        if "CIGAR BUTT" in status_ncav:
            s = 100
        elif "MURAH" in status_ncav:
            s = 70
        else:
            s = 20
        skor_komponen["ncav_test"] = s

        # ── Earnings Quality (15%) ────────────────────
        eq       = self.scorecard.get("earnings_quality", {})
        kons     = eq.get("konsistensi_laba", 0) * 40
        accrual  = 30 if eq.get("kualitas_accrual") == "TINGGI" else (
                   15 if eq.get("kualitas_accrual") == "SEDANG" else 0)
        eps_g    = min(30, eq.get("cagr_eps", 0) * 300)
        skor_komponen["earnings_quality"] = round(kons + accrual + eps_g)

        # ── Balance Sheet (15%) ───────────────────────
        bs      = self.scorecard.get("balance_sheet", {})
        der_s   = 40 if bs.get("der_ok") else 10
        ltd_s   = 30 if bs.get("ltd_ok") else 10
        ic_s    = 30 if bs.get("ic_ok")  else 0
        skor_komponen["balance_sheet_strength"] = der_s + ltd_s + ic_s

        # ── Dividend (10%) ────────────────────────────
        div      = self.scorecard.get("dividend", {})
        n_div    = div.get("tahun_bayar_dividen", 0)
        total_d  = div.get("total_tahun_data", 1)
        kons_d   = _div(n_div, total_d) * 60
        payout_s = 20 if div.get("payout_ok")   else 5
        cov_s    = 20 if div.get("coverage_ok")  else 0
        skor_komponen["dividend_consistency"] = round(kons_d + payout_s + cov_s)

        # ── Risk Penalty (5%) ────────────────────────
        # placeholder — akan diisi oleh risk_analyzer
        skor_komponen["risk_penalty"] = 80

        # ── Total Skor ────────────────────────────────
        bobot   = cfg.SCORECARD_WEIGHTS
        total   = 0.0
        for kunci, skor in skor_komponen.items():
            b_key = kunci if kunci in bobot else kunci.replace("_penalty", "_score")
            total += skor * bobot.get(b_key, bobot.get(kunci, 0))

        total = min(100, max(0, round(total)))

        # tentukan grade
        grade = "F"
        for g, info in cfg.GRADE.items():
            if total >= info["min"]:
                grade = g
                break

        self.scorecard["skor_per_komponen"] = skor_komponen
        self.scorecard["total_skor"]        = total
        self.scorecard["grade"]             = grade
        self.scorecard["label"]             = cfg.GRADE[grade]["label"]

        # sorting komponen berdasarkan skor
        self.scorecard["ranking_komponen"] = sorted(
            skor_komponen.items(), key=lambda x: x[1], reverse=True
        )

        self.riwayat.push(f"scorecard:total={total}|grade={grade}")

    # ──────────────────────────────────────────────────
    # HITUNG PER TAHUN (untuk linked list)
    # ──────────────────────────────────────────────────

    def _hitung_per_tahun(self, b, lr, harga):
        """Hitung Graham Number dan MoS untuk setiap tahun historis."""
        eps    = lr.eps
        bvs    = b.book_value_per_saham()
        gn     = _safe_sqrt(cfg.GRAHAM["graham_multiplier"] * eps * bvs)
        mos    = _div(gn - harga, gn)
        ncav   = b.ncav_per_saham()
        cr     = _div(b.total_aset_lancar, b.total_liabilitas_lancar)
        der    = _div(b.total_liabilitas, b.total_ekuitas)
        pe     = _div(harga, eps)
        pb     = _div(harga, bvs)

        return {
            "graham_number":    gn,
            "margin_of_safety": mos,
            "ncav_per_saham":   ncav,
            "current_ratio":    cr,
            "der":              der,
            "pe_ratio":         pe,
            "pb_ratio":         pb,
        }

    # ──────────────────────────────────────────────────
    # SEARCHING
    # ──────────────────────────────────────────────────

    def cari_tahun_mos_terbaik(self):
        """Cari tahun dengan MoS tertinggi via SLL."""
        best_tahun, best_mos = None, None
        cur = self.rantai.head
        while cur:
            mos = cur.hasil.get("margin_of_safety", None)
            if mos is not None:
                if best_mos is None or mos > best_mos:
                    best_tahun = cur.tahun
                    best_mos   = mos
            cur = cur.next
        return best_tahun, best_mos

    def cari_kriteria(self, nama_kriteria):
        """Cari hasil kriteria via Hash Table O(1)."""
        kunci = f"{self.ticker}_kriteria_{nama_kriteria}"
        return self.lookup.get(kunci)

    # ──────────────────────────────────────────────────
    # SORTING
    # ──────────────────────────────────────────────────

    def urutkan_tahun_by_mos(self, ascending=False):
        """Urutkan tahun berdasarkan Margin of Safety."""
        data = [
            (d["tahun"], d.get("margin_of_safety", 0))
            for d in self.hasil_per_tahun
        ]
        data.sort(key=lambda x: x[1], reverse=not ascending)
        return data

    def ranking_komponen(self):
        """Return komponen scorecard terurut dari skor tertinggi."""
        return self.scorecard.get("ranking_komponen", [])

    # ──────────────────────────────────────────────────
    # TAMPILKAN HASIL
    # ──────────────────────────────────────────────────

    def tampilkan(self):
        """Cetak hasil analisis Graham ke terminal."""
        print()
        print("=" * 60)
        print(f"  ANALISIS GRAHAM — {self.data.profil.nama} ({self.ticker})")
        print("=" * 60)

        # Scorecard utama
        print(f"\n  GRAHAM SCORECARD")
        print("  " + "-" * 40)
        for nama, skor in self.scorecard.get("skor_per_komponen", {}).items():
            bobot = cfg.SCORECARD_WEIGHTS.get(nama, 0)
            print(f"  {nama:<28}: {skor:>3}/100  (bobot {bobot*100:.0f}%)")
        print("  " + "-" * 40)
        print(f"  {'TOTAL SKOR':<28}: {self.scorecard.get('total_skor', 0):>3}/100")
        print(f"  {'GRADE':<28}: {self.scorecard.get('grade','?')} — "
              f"{self.scorecard.get('label','')}")

        # Valuasi
        print(f"\n  VALUASI")
        print("  " + "-" * 40)
        harga = self.data.profil.harga_pasar
        items_valuasi = [
            ("Graham Number",    "graham_number",    "Rp"),
            ("EPV per Saham",    "epv_per_saham",    "Rp"),
            ("DCF per Saham",    "dcf_per_saham",    "Rp"),
            ("Nilai Intrinsik",  "nilai_intrinsik_konservatif", "Rp"),
            ("Harga Pasar",      None,               "Rp"),
            ("Margin of Safety", "margin_of_safety_final", "%"),
        ]
        for label, kunci, unit in items_valuasi:
            if kunci is None:
                nilai = harga
            else:
                nilai = self.valuasi.get(kunci, 0)
            if unit == "%":
                print(f"  {label:<28}: {nilai*100:>8.1f}%")
            else:
                print(f"  {label:<28}: Rp {nilai:>12,.0f}")
        print(f"  {'Rekomendasi':<28}: {self.valuasi.get('rekomendasi_mos','')}")

        # 7 Kriteria
        print(f"\n  7 KRITERIA DEFENSIVE INVESTOR")
        print("  " + "-" * 40)
        deskripsi = {
            "kriteria_1": "Ukuran perusahaan memadai",
            "kriteria_2": f"Current Ratio >= {cfg.GRAHAM['min_current_ratio']}x",
            "kriteria_3": "Stabilitas laba (tidak rugi)",
            "kriteria_4": f"Dividen konsisten >= {cfg.GRAHAM['min_years_data']} tahun",
            "kriteria_5": f"Pertumbuhan EPS >= {cfg.GRAHAM['min_eps_growth_10yr']*100:.0f}%",
            "kriteria_6": f"P/E <= {cfg.GRAHAM['max_pe_ratio']}x",
            "kriteria_7": f"P/BV <= {cfg.GRAHAM['max_pb_ratio']}x",
        }
        for nama, lulus in self.scorecard.get("kriteria_7", {}).items():
            tanda = "LULUS" if lulus else "GAGAL"
            desc  = deskripsi.get(nama, nama)
            print(f"  [{tanda}] {desc}")
        skor_k7  = self.scorecard.get("skor_kriteria_7", 0)
        total_k7 = self.scorecard.get("total_kriteria_7", 7)
        print(f"  Skor: {skor_k7}/{total_k7}")

        # Tren MoS historis (dari DLL)
        print(f"\n  TREN GRAHAM NUMBER & MoS")
        print("  " + "-" * 40)
        delta = self.navigasi.perubahan("margin_of_safety")
        for tahun, nilai, arah in delta:
            arah_str = f"({arah})" if arah != "-" else ""
            print(f"  {tahun} : MoS {nilai*100:>6.1f}%  {arah_str}")

        # Window 3 tahun (CLL)
        print(f"\n  WINDOW 3 TAHUN TERAKHIR")
        print("  " + "-" * 40)
        for tahun, hasil in self.rotasi.window(3):
            gn  = hasil.get("graham_number", 0)
            mos = hasil.get("margin_of_safety", 0)
            print(f"  {tahun} | GN: Rp {gn:,.0f} | MoS: {mos*100:.1f}%")

        print()

    # ──────────────────────────────────────────────────
    # FILE HANDLER
    # ──────────────────────────────────────────────────

    def simpan(self, format_file="txt"):
        tanggal   = datetime.today().strftime(cfg.OUTPUT_DATE_FORMAT)
        nama_file = f"{self.ticker}_graham_{tanggal}.{format_file}"
        path      = cfg.OUTPUTS_DIR / nama_file

        if format_file == "json":
            self._simpan_json(path)
        else:
            self._simpan_txt(path)

        print(f"  Disimpan: {path}")
        self.riwayat.push(f"simpan:{path}")
        return path

    def _simpan_txt(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write(f"LAPORAN ANALISIS GRAHAM\n")
            f.write(f"{self.data.profil.nama} ({self.ticker})\n")
            f.write(f"Tanggal : {datetime.today().strftime('%d %b %Y')}\n")
            f.write("=" * 60 + "\n\n")

            # scorecard
            f.write("GRAHAM SCORECARD\n")
            f.write("-" * 40 + "\n")
            for nama, skor in self.scorecard.get("skor_per_komponen", {}).items():
                bobot = cfg.SCORECARD_WEIGHTS.get(nama, 0)
                f.write(f"  {nama:<28}: {skor:>3}/100  [{bobot*100:.0f}%]\n")
            f.write(f"  {'TOTAL':<28}: "
                    f"{self.scorecard.get('total_skor',0):>3}/100\n")
            f.write(f"  GRADE : {self.scorecard.get('grade','?')} — "
                    f"{self.scorecard.get('label','')}\n\n")

            # valuasi
            f.write("VALUASI\n")
            f.write("-" * 40 + "\n")
            harga = self.data.profil.harga_pasar
            for kunci, label, unit in [
                ("graham_number",    "Graham Number",   "Rp"),
                ("epv_per_saham",    "EPV per Saham",   "Rp"),
                ("dcf_per_saham",    "DCF per Saham",   "Rp"),
                ("nilai_intrinsik_konservatif", "Nilai Intrinsik", "Rp"),
                ("margin_of_safety_final",      "Margin of Safety", "%"),
            ]:
                nilai = self.valuasi.get(kunci, 0)
                if unit == "%":
                    f.write(f"  {label:<28}: {nilai*100:.1f}%\n")
                else:
                    f.write(f"  {label:<28}: Rp {nilai:,.0f}\n")
            f.write(f"  {'Harga Pasar':<28}: Rp {harga:,.0f}\n")
            f.write(f"  {'Rekomendasi':<28}: "
                    f"{self.valuasi.get('rekomendasi_mos','')}\n\n")

            # 7 kriteria
            f.write("7 KRITERIA DEFENSIVE INVESTOR\n")
            f.write("-" * 40 + "\n")
            for nama, lulus in self.scorecard.get("kriteria_7", {}).items():
                tanda = "LULUS" if lulus else "GAGAL"
                f.write(f"  [{tanda}] {nama}\n")
            f.write(f"  Skor : {self.scorecard.get('skor_kriteria_7',0)}"
                    f"/{self.scorecard.get('total_kriteria_7',7)}\n\n")

            # riwayat stack
            f.write("RIWAYAT KALKULASI\n")
            f.write("-" * 40 + "\n")
            tmp = []
            while not self.riwayat.kosong():
                tmp.append(self.riwayat.pop())
            for item in reversed(tmp):
                f.write(f"  {item}\n")
                self.riwayat.push(item)

    def _simpan_json(self, path):
        output = {
            "ticker":    self.ticker,
            "nama":      self.data.profil.nama,
            "tanggal":   datetime.today().strftime(cfg.OUTPUT_DATE_FORMAT),
            "scorecard": {
                "skor_per_komponen": self.scorecard.get("skor_per_komponen", {}),
                "total_skor":        self.scorecard.get("total_skor", 0),
                "grade":             self.scorecard.get("grade", ""),
                "label":             self.scorecard.get("label", ""),
            },
            "valuasi":        self.valuasi,
            "kriteria_7":     self.scorecard.get("kriteria_7", {}),
            "ncav":           self.scorecard.get("ncav", {}),
            "earnings_quality": self.scorecard.get("earnings_quality", {}),
            "balance_sheet":  self.scorecard.get("balance_sheet", {}),
            "dividend":       self.scorecard.get("dividend", {}),
            "historis":       self.hasil_per_tahun,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

    def baca_hasil(self, path):
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
