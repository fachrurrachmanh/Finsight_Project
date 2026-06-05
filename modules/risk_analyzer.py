"""
modules/risk_analyzer.py
=========================
Analisis risiko keuangan perusahaan.

Mencakup:
  - Risiko Likuiditas
  - Risiko Leverage / Solvabilitas
  - Risiko Operasional
  - Altman Z-Score (kebangkrutan)
  - Springate S-Score (kebangkrutan)
  - Beneish M-Score (manipulasi laba)
  - Risiko Pertumbuhan
  - Risk Dashboard (agregasi)

Struktur data (rubrik):
  - Single Linked List   : rantai RiskNode per tahun
  - Double Linked List   : perbandingan risiko tahun ini vs lalu
  - Circular Linked List : rotasi window periode risiko
  - Stack                : riwayat kalkulasi
  - Queue                : antrian modul risiko yang diproses
  - Hash Table           : lookup skor risiko O(1)
  - Tree                 : hierarki kategori risiko
  - List/Tuple/Set/Dict  : wadah hasil
  - Sorting              : ranking risiko tertinggi
  - Searching            : cari tahun paling berisiko
  - Rekursif             : trend risiko, rata-rata skor
  - File Handler         : simpan hasil ke file
  - OOP                  : class RiskAnalyzer
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
from sort_utils import merge_sort


# ══════════════════════════════════════════════════════
# HELPER
# ══════════════════════════════════════════════════════

def _div(a, b, default=0.0):
    return a / b if b != 0 else default

def _pct(nilai):
    return nilai * 100


# ══════════════════════════════════════════════════════
# SINGLE LINKED LIST — rantai skor risiko per tahun
# ══════════════════════════════════════════════════════

class RiskNode:
    def __init__(self, tahun, skor: dict):
        self.tahun = tahun
        self.skor  = skor    # { nama_risiko: nilai }
        self.next  = None


class SingleLinkedList:
    def __init__(self):
        self.head = None

    def tambah(self, tahun, skor: dict):
        node = RiskNode(tahun, skor)
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
# DOUBLE LINKED LIST — perbandingan risiko antar tahun
# ══════════════════════════════════════════════════════

class DoubleNode:
    def __init__(self, tahun, skor: dict):
        self.tahun = tahun
        self.skor  = skor
        self.next  = None
        self.prev  = None


class DoubleLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def tambah(self, tahun, skor: dict):
        node = DoubleNode(tahun, skor)
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
        Lacak perubahan nilai risiko dari tahun ke tahun.
        Return: list of (tahun, nilai, arah)
        arah: 'memburuk' | 'membaik' | 'tetap' | '-'

        Khusus risiko: naik = memburuk, turun = membaik
        (kebalikan dari rasio profitabilitas)
        """
        hasil, cur = [], self.head
        while cur:
            nilai = cur.skor.get(kunci, 0)
            if cur.prev:
                lalu = cur.prev.skor.get(kunci, 0)
                if nilai > lalu:
                    arah = "memburuk"
                elif nilai < lalu:
                    arah = "membaik"
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
    def __init__(self, tahun, skor: dict):
        self.tahun = tahun
        self.skor  = skor
        self.next  = None


class CircularLinkedList:
    def __init__(self):
        self.head   = None
        self.ukuran = 0

    def tambah(self, tahun, skor: dict):
        node = CircularNode(tahun, skor)
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
            hasil.append((cur.tahun, cur.skor))
            cur = cur.next
        return hasil


# ══════════════════════════════════════════════════════
# STACK — riwayat kalkulasi
# ══════════════════════════════════════════════════════

class Stack:
    def __init__(self):
        self._data = []

    def push(self, item):  self._data.append(item)
    def pop(self):         return self._data.pop() if self._data else None
    def peek(self):        return self._data[-1] if self._data else None
    def kosong(self):      return len(self._data) == 0
    def ukuran(self):      return len(self._data)


# ══════════════════════════════════════════════════════
# QUEUE — antrian modul risiko
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
# HASH TABLE — lookup skor risiko O(1)
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
# TREE — hierarki kategori risiko
# ══════════════════════════════════════════════════════

class TreeNode:
    def __init__(self, nama, bobot=0.0):
        self.nama     = nama
        self.bobot    = bobot
        self.children = []
        self.indikator = []   # list nama indikator di kategori ini

    def tambah_child(self, child):
        self.children.append(child)
        return child

    def tambah_indikator(self, nama):
        self.indikator.append(nama)


def buat_pohon_risiko():
    """
    Pohon hierarki kategori risiko keuangan.

    Risk Dashboard
    ├── Likuiditas        (bobot 25%)
    │   ├── current_ratio
    │   ├── quick_ratio
    │   ├── cash_ratio
    │   └── days_cash
    ├── Leverage          (bobot 25%)
    │   ├── der
    │   ├── interest_coverage
    │   └── net_debt_ebitda
    ├── Operasional       (bobot 20%)
    │   ├── operating_leverage
    │   ├── ebitda_margin_trend
    │   └── revenue_volatility
    ├── Kebangkrutan      (bobot 15%)
    │   ├── altman_z
    │   └── springate_s
    └── Manipulasi        (bobot 15%)
        ├── beneish_m
        └── accrual_ratio
    """
    root = TreeNode("Risk Dashboard", bobot=1.0)

    liq = root.tambah_child(TreeNode("Likuiditas", bobot=0.25))
    liq.tambah_indikator("current_ratio")
    liq.tambah_indikator("quick_ratio")
    liq.tambah_indikator("cash_ratio")
    liq.tambah_indikator("days_cash")

    lev = root.tambah_child(TreeNode("Leverage", bobot=0.25))
    lev.tambah_indikator("der")
    lev.tambah_indikator("interest_coverage")
    lev.tambah_indikator("net_debt_ebitda")

    ops = root.tambah_child(TreeNode("Operasional", bobot=0.20))
    ops.tambah_indikator("operating_leverage")
    ops.tambah_indikator("ebitda_margin")
    ops.tambah_indikator("revenue_volatility")

    bangkrut = root.tambah_child(TreeNode("Kebangkrutan", bobot=0.15))
    bangkrut.tambah_indikator("altman_z")
    bangkrut.tambah_indikator("springate_s")

    manip = root.tambah_child(TreeNode("Manipulasi", bobot=0.15))
    manip.tambah_indikator("beneish_m")
    manip.tambah_indikator("accrual_ratio")

    return root


def tampilkan_pohon(node, indent=0):
    """Tampilkan pohon risiko secara rekursif."""
    prefix    = "  " * indent
    bobot_str = f" [{node.bobot*100:.0f}%]" if node.bobot > 0 else ""
    print(f"{prefix}{node.nama}{bobot_str}")
    for ind in node.indikator:
        print(f"{prefix}  · {ind}")
    for child in node.children:
        tampilkan_pohon(child, indent + 1)


def cari_kategori_risiko(root, nama_indikator):
    """Searching di tree — cari kategori dari sebuah indikator."""
    for child in root.children:
        if nama_indikator in child.indikator:
            return child.nama
    return None


# ══════════════════════════════════════════════════════
# REKURSIF
# ══════════════════════════════════════════════════════

def rata_rata_rekursif(data, index=0, total=0.0):
    """Hitung rata-rata list secara rekursif."""
    if not data:
        return 0.0
    if index == len(data):
        return total / len(data)
    return rata_rata_rekursif(data, index + 1, total + data[index])


def std_dev_rekursif(data, avg, index=0, total=0.0):
    """Hitung standar deviasi secara rekursif."""
    if not data or len(data) < 2:
        return 0.0
    if index == len(data):
        return (total / len(data)) ** 0.5
    return std_dev_rekursif(data, avg, index + 1, total + (data[index] - avg) ** 2)


def hitung_skor_risiko_rekursif(skor_list, bobot_list, index=0, total=0.0):
    """
    Agregasi skor risiko tertimbang secara rekursif.
    skor_list  : list skor per kategori (0-100, makin tinggi makin berisiko)
    bobot_list : list bobot per kategori
    """
    if index == len(skor_list):
        return min(100, max(0, total))
    return hitung_skor_risiko_rekursif(
        skor_list, bobot_list,
        index + 1,
        total + skor_list[index] * bobot_list[index]
    )


def tren_risiko_rekursif(skor_list, index=1, naik=0, turun=0):
    """
    Hitung tren risiko secara rekursif.
    Return: ('memburuk'|'membaik'|'stabil', selisih_rata)
    """
    if index >= len(skor_list):
        if naik > turun:
            return "memburuk", naik - turun
        elif turun > naik:
            return "membaik", turun - naik
        else:
            return "stabil", 0
    delta = skor_list[index] - skor_list[index - 1]
    if delta > 0:
        naik += 1
    elif delta < 0:
        turun += 1
    return tren_risiko_rekursif(skor_list, index + 1, naik, turun)


def cagr_rekursif(awal, akhir, n):
    """CAGR rekursif."""
    if awal <= 0 or akhir <= 0 or n <= 0:
        return 0.0
    if n == 1:
        return (akhir / awal) - 1.0
    tengah = awal * ((akhir / awal) ** (1.0 / n))
    return cagr_rekursif(tengah, akhir, n - 1)


# ══════════════════════════════════════════════════════
# KELAS UTAMA
# ══════════════════════════════════════════════════════

class RiskAnalyzer:
    """
    Analisis risiko keuangan perusahaan dari CompanyData.

    Contoh:
        analyzer = RiskAnalyzer(data)
        analyzer.analisis()
        analyzer.tampilkan()
        analyzer.simpan()
    """

    def __init__(self, data: CompanyData):
        self.data   = data
        self.ticker = data.profil.ticker

        # struktur data
        self.rantai   = SingleLinkedList()
        self.navigasi = DoubleLinkedList()
        self.rotasi   = CircularLinkedList()
        self.riwayat  = Stack()
        self.antrian  = Queue()
        self.lookup   = HashTable()
        self.pohon    = buat_pohon_risiko()

        # hasil
        self.hasil_per_tahun: list[dict] = []
        self.dashboard:       dict       = {}
        self.red_flags:       list       = []
        self.kategori_risiko: set        = set()
        self.skor_per_kategori: dict     = {}

    # ──────────────────────────────────────────────────
    # TITIK MASUK
    # ──────────────────────────────────────────────────

    def analisis(self):
        """Jalankan seluruh analisis risiko."""
        print(f"\n  Analisis Risiko — {self.ticker}...")

        b  = self.data.neraca_terbaru()
        lr = self.data.laba_rugi_terbaru()
        cf = self.data.arus_kas_terbaru()

        if not b or not lr:
            print("  ERROR: Data tidak cukup.")
            return self

        # antrian modul risiko
        for modul in ["likuiditas", "leverage", "operasional",
                      "altman_z", "springate_s", "beneish_m",
                      "pertumbuhan", "dashboard"]:
            self.antrian.enqueue(modul)

        # proses antrian
        while not self.antrian.kosong():
            modul = self.antrian.dequeue()
            self.riwayat.push(f"mulai:{modul}")

            if modul == "likuiditas":
                self._analisis_likuiditas(b, lr)
            elif modul == "leverage":
                self._analisis_leverage(b, lr)
            elif modul == "operasional":
                self._analisis_operasional(lr)
            elif modul == "altman_z":
                self._hitung_altman_z(b, lr)
            elif modul == "springate_s":
                self._hitung_springate_s(b, lr, cf)
            elif modul == "beneish_m":
                self._hitung_beneish_m(b, lr, cf)
            elif modul == "pertumbuhan":
                self._analisis_pertumbuhan()
            elif modul == "dashboard":
                self._hitung_dashboard()

            self.riwayat.push(f"selesai:{modul}")

        # isi linked list historis
        for i, b_hist in enumerate(self.data.neraca):
            lr_hist = self.data.laba_rugi[i] if i < len(self.data.laba_rugi) else None
            cf_hist = self.data.arus_kas[i]  if i < len(self.data.arus_kas)  else None
            if not lr_hist:
                continue

            skor_tahun = self._skor_per_tahun(b_hist, lr_hist, cf_hist)
            self.rantai.tambah(b_hist.tahun, skor_tahun)
            self.navigasi.tambah(b_hist.tahun, skor_tahun)
            self.rotasi.tambah(b_hist.tahun, skor_tahun)
            self.hasil_per_tahun.append({"tahun": b_hist.tahun, **skor_tahun})

            for kunci, nilai in skor_tahun.items():
                self.lookup.set(f"{self.ticker}_{b_hist.tahun}_{kunci}", nilai)

        # kumpulkan kategori unik (set)
        for child in self.pohon.children:
            self.kategori_risiko.add(child.nama)

        print("  Selesai.")
        return self

    # ──────────────────────────────────────────────────
    # 1. RISIKO LIKUIDITAS
    # ──────────────────────────────────────────────────

    def _analisis_likuiditas(self, b, lr):
        cr  = _div(b.total_aset_lancar, b.total_liabilitas_lancar)
        qr  = _div(b.total_aset_lancar - b.persediaan, b.total_liabilitas_lancar)
        csr = _div(b.kas_setara_kas, b.total_liabilitas_lancar)
        dch = _div(b.kas_setara_kas * 365, lr.beban_operasional)

        # skor risiko: makin rendah rasio → makin tinggi risiko (0-100)
        def skor_cr(v):
            if v >= 2.0: return 10
            if v >= 1.5: return 30
            if v >= 1.0: return 60
            return 90

        def skor_qr(v):
            if v >= 1.0: return 10
            if v >= 0.7: return 35
            if v >= 0.5: return 65
            return 90

        def skor_csr(v):
            if v >= cfg.RISK["min_cash_ratio"]: return 10
            if v >= 0.10: return 50
            return 85

        def skor_dch(v):
            if v >= 90:  return 10
            if v >= 30:  return 40
            if v >= 15:  return 70
            return 90

        skor = rata_rata_rekursif([
            skor_cr(cr), skor_qr(qr), skor_csr(csr), skor_dch(dch)
        ])

        # red flags
        if cr < cfg.GRAHAM["min_current_ratio"]:
            self.red_flags.append(
                f"Current Ratio {cr:.2f}x < {cfg.GRAHAM['min_current_ratio']}x"
            )
        if csr < cfg.RISK["min_cash_ratio"]:
            self.red_flags.append(f"Cash Ratio rendah: {csr:.2f}x")

        self.dashboard["likuiditas"] = {
            "current_ratio":  cr,
            "quick_ratio":    qr,
            "cash_ratio":     csr,
            "days_cash":      dch,
            "skor_risiko":    round(skor),
        }
        self.skor_per_kategori["Likuiditas"] = round(skor)
        self.lookup.set(f"{self.ticker}_skor_likuiditas", round(skor))
        self.riwayat.push(f"likuiditas:cr={cr:.2f}|skor={skor:.0f}")

    # ──────────────────────────────────────────────────
    # 2. RISIKO LEVERAGE
    # ──────────────────────────────────────────────────

    def _analisis_leverage(self, b, lr):
        der  = _div(b.total_liabilitas, b.total_ekuitas)
        dar  = _div(b.total_liabilitas, b.total_aset)
        ic   = _div(lr.ebit, lr.beban_bunga)
        nde  = _div(b.net_debt(), lr.ebitda)

        def skor_der(v):
            if v <= 0.5: return 10
            if v <= 1.0: return 25
            if v <= 2.0: return 55
            if v <= 3.0: return 75
            return 95

        def skor_ic(v):
            if v <= 0:   return 95
            if v >= 5.0: return 10
            if v >= 3.0: return 30
            if v >= 1.5: return 60
            return 85

        def skor_nde(v):
            if v <= 1.0: return 10
            if v <= 2.0: return 30
            if v <= 3.0: return 55
            if v <= 5.0: return 75
            return 95

        skor = rata_rata_rekursif([skor_der(der), skor_ic(ic), skor_nde(nde)])

        if der > cfg.GRAHAM["max_der"]:
            self.red_flags.append(f"DER {der:.2f}x melebihi threshold {cfg.GRAHAM['max_der']}x")
        if ic < cfg.RISK["min_interest_coverage"] and lr.beban_bunga > 0:
            self.red_flags.append(
                f"Interest Coverage {ic:.2f}x < {cfg.RISK['min_interest_coverage']}x"
            )
        if nde > cfg.RISK["max_net_debt_ebitda"]:
            self.red_flags.append(
                f"Net Debt/EBITDA {nde:.2f}x > {cfg.RISK['max_net_debt_ebitda']}x"
            )

        self.dashboard["leverage"] = {
            "der":              der,
            "dar":              dar,
            "interest_coverage": ic,
            "net_debt_ebitda":  nde,
            "skor_risiko":      round(skor),
        }
        self.skor_per_kategori["Leverage"] = round(skor)
        self.lookup.set(f"{self.ticker}_skor_leverage", round(skor))
        self.riwayat.push(f"leverage:der={der:.2f}|ic={ic:.2f}|skor={skor:.0f}")

    # ──────────────────────────────────────────────────
    # 3. RISIKO OPERASIONAL
    # ──────────────────────────────────────────────────

    def _analisis_operasional(self, lr):
        pendapatan_list = self.data.pendapatan_historis()
        laba_list       = [i.laba_bersih for i in self.data.laba_rugi]
        ebitda_list     = [i.ebitda      for i in self.data.laba_rugi]

        # volatilitas pendapatan (coefficient of variation)
        avg_rev = rata_rata_rekursif(pendapatan_list)
        std_rev = std_dev_rekursif(pendapatan_list, avg_rev)
        cv_rev  = _div(std_rev, avg_rev)

        # tren EBITDA margin
        margin_list = [_div(e, p) for e, p in zip(ebitda_list, pendapatan_list)]
        avg_margin  = rata_rata_rekursif(margin_list)
        tren_margin, _ = tren_risiko_rekursif(margin_list)

        # operating leverage = % perubahan EBIT / % perubahan pendapatan
        if len(pendapatan_list) >= 2 and pendapatan_list[-2] > 0:
            pct_rev  = _div(pendapatan_list[-1] - pendapatan_list[-2],
                            pendapatan_list[-2])
            pct_ebit = _div(lr.ebit - self.data.laba_rugi[-2].ebit,
                            abs(self.data.laba_rugi[-2].ebit))
            op_lev   = _div(pct_ebit, pct_rev)
        else:
            op_lev = 0.0

        def skor_cv(v):
            if v <= 0.05: return 10
            if v <= 0.10: return 30
            if v <= 0.20: return 60
            return 85

        def skor_margin(v):
            if v >= 0.25: return 10
            if v >= 0.15: return 30
            if v >= 0.05: return 60
            return 85

        skor = rata_rata_rekursif([
            skor_cv(cv_rev),
            skor_margin(avg_margin),
            20 if tren_margin == "membaik" else (50 if tren_margin == "stabil" else 75),
        ])

        self.dashboard["operasional"] = {
            "revenue_volatility":  cv_rev,
            "avg_ebitda_margin":   avg_margin,
            "tren_ebitda_margin":  tren_margin,
            "operating_leverage":  op_lev,
            "skor_risiko":         round(skor),
        }
        self.skor_per_kategori["Operasional"] = round(skor)
        self.lookup.set(f"{self.ticker}_skor_operasional", round(skor))
        self.riwayat.push(f"operasional:cv={cv_rev:.3f}|skor={skor:.0f}")

    # ──────────────────────────────────────────────────
    # 4. ALTMAN Z-SCORE
    # ──────────────────────────────────────────────────

    def _hitung_altman_z(self, b, lr):
        """
        Altman Z-Score untuk perusahaan manufaktur/non-keuangan:
        Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5

        X1 = Working Capital / Total Aset
        X2 = Laba Ditahan / Total Aset
        X3 = EBIT / Total Aset
        X4 = Market Cap / Total Liabilitas
        X5 = Pendapatan / Total Aset
        """
        ta  = b.total_aset
        wc  = b.working_capital()
        re  = b.laba_ditahan
        mc  = self.data.profil.harga_pasar * b.jumlah_saham_beredar

        x1 = _div(wc,        ta)
        x2 = _div(re,        ta)
        x3 = _div(lr.ebit,   ta)
        x4 = _div(mc,        b.total_liabilitas)
        x5 = _div(lr.pendapatan, ta)

        z = 1.2*x1 + 1.4*x2 + 3.3*x3 + 0.6*x4 + 1.0*x5

        if z > cfg.RISK["altman_safe"]:
            status = "AMAN"
            skor   = 10
        elif z > cfg.RISK["altman_grey"]:
            status = "ABU-ABU"
            skor   = 55
        else:
            status = "BAHAYA"
            skor   = 90
            self.red_flags.append(f"Altman Z-Score {z:.2f} — zona BAHAYA (<{cfg.RISK['altman_grey']})")

        self.dashboard["altman_z"] = {
            "x1": x1, "x2": x2, "x3": x3, "x4": x4, "x5": x5,
            "z_score": z,
            "status":  status,
            "skor_risiko": skor,
        }
        self.skor_per_kategori["Kebangkrutan_Altman"] = skor
        self.lookup.set(f"{self.ticker}_altman_z", z)
        self.lookup.set(f"{self.ticker}_altman_status", status)
        self.riwayat.push(f"altman_z:{z:.2f}|{status}")

    # ──────────────────────────────────────────────────
    # 5. SPRINGATE S-SCORE
    # ──────────────────────────────────────────────────

    def _hitung_springate_s(self, b, lr, cf):
        """
        Springate S-Score:
        S = 1.03*A + 3.07*B + 0.66*C + 0.4*D

        A = Working Capital / Total Aset
        B = EBIT / Total Aset
        C = EBT / Total Liabilitas Lancar
        D = Pendapatan / Total Aset
        """
        ta  = b.total_aset
        wc  = b.working_capital()
        tll = b.total_liabilitas_lancar

        a = _div(wc,           ta)
        b_val = _div(lr.ebit,  ta)
        c = _div(lr.laba_sebelum_pajak, tll)
        d = _div(lr.pendapatan, ta)

        s = 1.03*a + 3.07*b_val + 0.66*c + 0.4*d

        if s >= cfg.RISK["springate_threshold"]:
            status = "SEHAT"
            skor   = 10
        else:
            status = "BERPOTENSI BANGKRUT"
            skor   = 85
            self.red_flags.append(
                f"Springate S-Score {s:.2f} < {cfg.RISK['springate_threshold']}"
            )

        self.dashboard["springate_s"] = {
            "a": a, "b": b_val, "c": c, "d": d,
            "s_score":     s,
            "status":      status,
            "skor_risiko": skor,
        }
        self.skor_per_kategori["Kebangkrutan_Springate"] = skor
        self.lookup.set(f"{self.ticker}_springate_s", s)
        self.riwayat.push(f"springate_s:{s:.2f}|{status}")

    # ──────────────────────────────────────────────────
    # 6. BENEISH M-SCORE (deteksi manipulasi laba)
    # ──────────────────────────────────────────────────

    def _hitung_beneish_m(self, b, lr, cf):
        """
        Beneish M-Score — 8 variabel indikator manipulasi laba.
        M > -1.78 → potensi manipulasi

        Membutuhkan minimal 2 tahun data untuk perbandingan t vs t-1.
        """
        if len(self.data.neraca) < 2 or len(self.data.laba_rugi) < 2:
            self.dashboard["beneish_m"] = {
                "m_score":     None,
                "status":      "DATA TIDAK CUKUP (butuh >= 2 tahun)",
                "skor_risiko": 50,
            }
            self.riwayat.push("beneish_m:data_kurang")
            return

        b0  = self.data.neraca[-2]
        b1  = self.data.neraca[-1]
        lr0 = self.data.laba_rugi[-2]
        lr1 = self.data.laba_rugi[-1]

        # Days Sales Receivable Index
        dsr0  = _div(b0.piutang_usaha, lr0.pendapatan) * 365
        dsr1  = _div(b1.piutang_usaha, lr1.pendapatan) * 365
        dsri  = _div(dsr1, dsr0) if dsr0 != 0 else 1.0

        # Gross Margin Index
        gm0   = _div(lr0.laba_kotor, lr0.pendapatan)
        gm1   = _div(lr1.laba_kotor, lr1.pendapatan)
        gmi   = _div(gm0, gm1) if gm1 != 0 else 1.0

        # Asset Quality Index
        aq0   = _div(b0.total_aset - b0.total_aset_lancar - b0.aset_tetap_neto, b0.total_aset)
        aq1   = _div(b1.total_aset - b1.total_aset_lancar - b1.aset_tetap_neto, b1.total_aset)
        aqi   = _div(aq1, aq0) if aq0 != 0 else 1.0

        # Sales Growth Index
        sgi   = _div(lr1.pendapatan, lr0.pendapatan)

        # Depreciation Index
        dep0  = _div(b0.aset_tetap_neto, b0.aset_tetap_neto + lr0.beban_penyusutan) if lr0.beban_penyusutan != 0 else 1
        dep1  = _div(b1.aset_tetap_neto, b1.aset_tetap_neto + lr1.beban_penyusutan) if lr1.beban_penyusutan != 0 else 1
        depi  = _div(dep0, dep1) if dep1 != 0 else 1.0

        # Sales General Admin Index
        sga0  = _div(lr0.beban_operasional, lr0.pendapatan)
        sga1  = _div(lr1.beban_operasional, lr1.pendapatan)
        sgai  = _div(sga1, sga0) if sga0 != 0 else 1.0

        # Leverage Index
        lev0  = _div(b0.utang_jangka_pendek + b0.utang_jangka_panjang, b0.total_aset)
        lev1  = _div(b1.utang_jangka_pendek + b1.utang_jangka_panjang, b1.total_aset)
        lvgi  = _div(lev1, lev0) if lev0 != 0 else 1.0

        # Total Accruals to Total Assets
        cf_ops = self.data.arus_kas[-1].arus_kas_operasi if self.data.arus_kas else 0
        tata  = _div(lr1.laba_bersih - cf_ops, b1.total_aset)

        # M-Score formula
        m = (-4.84
             + 0.920  * dsri
             + 0.528  * gmi
             + 0.404  * aqi
             + 0.892  * sgi
             + 0.115  * depi
             - 0.172  * sgai
             + 4.679  * tata
             - 0.327  * lvgi)

        if m > cfg.RISK["beneish_threshold"]:
            status = "POTENSI MANIPULASI"
            skor   = 85
            self.red_flags.append(
                f"Beneish M-Score {m:.2f} > {cfg.RISK['beneish_threshold']} — "
                f"potensi manipulasi laba"
            )
        else:
            status = "TIDAK TERINDIKASI"
            skor   = 15

        self.dashboard["beneish_m"] = {
            "dsri": dsri, "gmi": gmi, "aqi": aqi, "sgi": sgi,
            "depi": depi, "sgai": sgai, "lvgi": lvgi, "tata": tata,
            "m_score":     m,
            "status":      status,
            "skor_risiko": skor,
        }
        self.skor_per_kategori["Manipulasi"] = skor
        self.lookup.set(f"{self.ticker}_beneish_m", m)
        self.riwayat.push(f"beneish_m:{m:.2f}|{status}")

    # ──────────────────────────────────────────────────
    # 7. RISIKO PERTUMBUHAN
    # ──────────────────────────────────────────────────

    def _analisis_pertumbuhan(self):
        pendapatan = self.data.pendapatan_historis()
        laba       = [lr.laba_bersih for lr in self.data.laba_rugi]
        fcf        = self.data.fcf_historis()
        eps        = self.data.eps_historis()

        def hitung_cagr(lst):
            if len(lst) >= 2 and lst[0] > 0 and lst[-1] > 0:
                return cagr_rekursif(lst[0], lst[-1], len(lst) - 1)
            return 0.0

        cagr_rev  = hitung_cagr(pendapatan)
        cagr_earn = hitung_cagr(laba)
        cagr_fcf  = hitung_cagr(fcf)
        cagr_eps  = hitung_cagr(eps)

        # FCF vs laba — jika laba jauh di atas FCF = red flag
        lr_terbaru = self.data.laba_rugi_terbaru()
        cf_terbaru = self.data.arus_kas_terbaru()
        if lr_terbaru and cf_terbaru:
            net_income = lr_terbaru.laba_bersih
            fcf_kini   = cf_terbaru.free_cash_flow()
            rasio_fcf_laba = _div(fcf_kini, net_income) if net_income > 0 else 0
            if net_income > 0 and rasio_fcf_laba < 0.5:
                self.red_flags.append(
                    f"FCF ({fcf_kini:,.0f}) jauh di bawah Laba Bersih "
                    f"({net_income:,.0f}) — kualitas laba dipertanyakan"
                )
        else:
            rasio_fcf_laba = 0.0

        # accrual ratio terbaru
        b_terbaru  = self.data.neraca_terbaru()
        accrual    = 0.0
        if lr_terbaru and cf_terbaru and b_terbaru:
            accrual = _div(lr_terbaru.laba_bersih - cf_terbaru.free_cash_flow(),
                           b_terbaru.total_aset)
            if abs(accrual) > cfg.RISK["accrual_ratio_danger"]:
                self.red_flags.append(
                    f"Accrual Ratio {accrual:.2%} > "
                    f"{cfg.RISK['accrual_ratio_danger']*100:.0f}% — hati-hati"
                )

        # skor risiko pertumbuhan — makin rendah CAGR → makin berisiko
        def skor_cagr(v):
            if v >= 0.10: return 10
            if v >= 0.05: return 30
            if v >= 0:    return 55
            return 85

        skor = rata_rata_rekursif([
            skor_cagr(cagr_rev),
            skor_cagr(cagr_earn),
            skor_cagr(cagr_fcf),
        ])

        self.dashboard["pertumbuhan"] = {
            "cagr_pendapatan":  cagr_rev,
            "cagr_laba_bersih": cagr_earn,
            "cagr_fcf":         cagr_fcf,
            "cagr_eps":         cagr_eps,
            "accrual_ratio":    accrual,
            "rasio_fcf_laba":   rasio_fcf_laba,
            "skor_risiko":      round(skor),
        }
        self.skor_per_kategori["Pertumbuhan"] = round(skor)
        self.lookup.set(f"{self.ticker}_skor_pertumbuhan", round(skor))
        self.riwayat.push(f"pertumbuhan:cagr_rev={cagr_rev:.3f}|skor={skor:.0f}")

    # ──────────────────────────────────────────────────
    # 8. RISK DASHBOARD (agregasi)
    # ──────────────────────────────────────────────────

    def _hitung_dashboard(self):
        """
        Agregasi semua skor menjadi Risk Score total (0-100).
        Bobot dari pohon risiko.
        Semakin tinggi skor → semakin berisiko.
        """
        bobot_map = {
            "Likuiditas":           0.25,
            "Leverage":             0.25,
            "Operasional":          0.20,
            "Kebangkrutan_Altman":  0.075,
            "Kebangkrutan_Springate": 0.075,
            "Manipulasi":           0.15,
            "Pertumbuhan":          0.00,  # informatif, tidak masuk skor utama
        }

        skor_list  = []
        bobot_list = []
        for kategori, bobot in bobot_map.items():
            if kategori in self.skor_per_kategori and bobot > 0:
                skor_list.append(self.skor_per_kategori[kategori])
                bobot_list.append(bobot)

        # normalisasi bobot
        total_bobot = sum(bobot_list)
        if total_bobot > 0:
            bobot_list = [b / total_bobot for b in bobot_list]

        # agregasi rekursif
        total_skor = hitung_skor_risiko_rekursif(skor_list, bobot_list)

        # tentukan level risiko
        if total_skor <= 25:
            level = "RENDAH"
        elif total_skor <= 50:
            level = "SEDANG"
        elif total_skor <= 75:
            level = "TINGGI"
        else:
            level = "KRITIS"

        # tren risiko historis
        skor_hist = [d.get("skor_total", 50) for d in self.hasil_per_tahun]
        tren, _ = tren_risiko_rekursif(skor_hist) if skor_hist else ("stabil", 0)

        self.dashboard["total"] = {
            "skor_risiko": round(total_skor),
            "level":       level,
            "tren":        tren,
            "jumlah_red_flag": len(self.red_flags),
        }

        self.lookup.set(f"{self.ticker}_risk_total",  round(total_skor))
        self.lookup.set(f"{self.ticker}_risk_level",  level)
        self.riwayat.push(f"dashboard:skor={total_skor:.0f}|level={level}")

    # ──────────────────────────────────────────────────
    # SKOR PER TAHUN (untuk linked list historis)
    # ──────────────────────────────────────────────────

    def _skor_per_tahun(self, b, lr, cf):
        """Hitung skor risiko ringkas untuk satu tahun."""
        cr  = _div(b.total_aset_lancar, b.total_liabilitas_lancar)
        der = _div(b.total_liabilitas, b.total_ekuitas)
        ic  = _div(lr.ebit, lr.beban_bunga)
        fcf = cf.free_cash_flow() if cf else 0

        # Altman Z ringkas
        ta  = b.total_aset
        wc  = b.working_capital()
        mc  = b.jumlah_saham_beredar * self.data.profil.harga_pasar
        z   = (1.2 * _div(wc, ta)
               + 1.4 * _div(b.laba_ditahan, ta)
               + 3.3 * _div(lr.ebit, ta)
               + 0.6 * _div(mc, b.total_liabilitas)
               + 1.0 * _div(lr.pendapatan, ta))

        skor_total = rata_rata_rekursif([
            90 if cr < 1.0 else (50 if cr < 2.0 else 10),
            90 if der > 3.0 else (50 if der > 1.0 else 10),
            85 if ic  < 1.5 else (40 if ic  < 3.0 else 10),
        ])

        return {
            "current_ratio":  cr,
            "der":            der,
            "interest_coverage": ic,
            "altman_z":       z,
            "free_cash_flow": fcf,
            "skor_total":     round(skor_total),
        }

    # ──────────────────────────────────────────────────
    # SEARCHING
    # ──────────────────────────────────────────────────

    def cari_tahun_paling_berisiko(self):
        """Cari tahun dengan skor risiko tertinggi via SLL."""
        best_tahun, best_skor = None, None
        cur = self.rantai.head
        while cur:
            skor = cur.skor.get("skor_total", 0)
            if best_skor is None or skor > best_skor:
                best_tahun = cur.tahun
                best_skor  = skor
            cur = cur.next
        return best_tahun, best_skor

    def cari_skor(self, kunci):
        """Cari skor risiko via Hash Table O(1)."""
        return self.lookup.get(f"{self.ticker}_{kunci}")

    # ──────────────────────────────────────────────────
    # SORTING
    # ──────────────────────────────────────────────────

    def urutkan_kategori_by_risiko(self, ascending=False):
        """
        Sorting — urutkan kategori risiko dari tertinggi ke terendah.
        Return: list of tuple (kategori, skor)
        """
        data = list(self.skor_per_kategori.items())
        data = merge_sort(data, key=lambda x: x[1], reverse=not ascending)
        return data

    def urutkan_tahun_by_risiko(self, ascending=False):
        """Urutkan tahun berdasarkan skor risiko total."""
        data = [(d["tahun"], d.get("skor_total", 0)) for d in self.hasil_per_tahun]
        data = merge_sort(data, key=lambda x: x[1], reverse=not ascending)
        return data

    def ranking_red_flags(self):
        """Kembalikan red flags diurutkan berdasarkan urutan kemunculan."""
        return [(i + 1, flag) for i, flag in enumerate(self.red_flags)]

    # ──────────────────────────────────────────────────
    # TAMPILKAN
    # ──────────────────────────────────────────────────

    def tampilkan(self):
        """Cetak hasil analisis risiko ke terminal."""
        total    = self.dashboard.get("total", {})
        skor     = total.get("skor_risiko", 0)
        level    = total.get("level", "-")

        print()
        print("=" * 60)
        print(f"  RISK DASHBOARD — {self.data.profil.nama} ({self.ticker})")
        print("=" * 60)

        # skor per kategori (sorting — tertinggi ke terendah)
        print(f"\n  SKOR RISIKO PER KATEGORI  (0=aman, 100=kritis)")
        print("  " + "-" * 40)
        for kategori, sk in self.urutkan_kategori_by_risiko():
            bar = "█" * (sk // 10) + "░" * (10 - sk // 10)
            print(f"  {kategori:<25}: {sk:>3}  {bar}")
        print("  " + "-" * 40)
        print(f"  {'TOTAL RISK SCORE':<25}: {skor:>3}  [{level}]")

        # detail per modul
        modul_list = [
            ("LIKUIDITAS",    "likuiditas",  ["current_ratio","quick_ratio","cash_ratio","days_cash"]),
            ("LEVERAGE",      "leverage",    ["der","dar","interest_coverage","net_debt_ebitda"]),
            ("ALTMAN Z-SCORE","altman_z",    ["z_score","status"]),
            ("SPRINGATE",     "springate_s", ["s_score","status"]),
            ("BENEISH M",     "beneish_m",   ["m_score","status"]),
            ("PERTUMBUHAN",   "pertumbuhan", ["cagr_pendapatan","cagr_laba_bersih","cagr_fcf","accrual_ratio"]),
        ]
        for judul, kunci, fields in modul_list:
            detail = self.dashboard.get(kunci, {})
            if not detail:
                continue
            print(f"\n  {judul}")
            print("  " + "-" * 40)
            for f in fields:
                val = detail.get(f)
                if val is None:
                    continue
                if isinstance(val, float):
                    if f in ("cagr_pendapatan","cagr_laba_bersih","cagr_fcf","accrual_ratio"):
                        print(f"    {f:<28}: {val*100:.2f}%")
                    elif f in ("current_ratio","quick_ratio","cash_ratio","der","dar",
                               "interest_coverage","net_debt_ebitda","operating_leverage"):
                        print(f"    {f:<28}: {val:.2f}x")
                    else:
                        print(f"    {f:<28}: {val:.4f}")
                else:
                    print(f"    {f:<28}: {val}")

        # red flags
        print(f"\n  RED FLAGS ({len(self.red_flags)} ditemukan)")
        print("  " + "-" * 40)
        if self.red_flags:
            for i, flag in enumerate(self.red_flags, 1):
                print(f"  [{i}] {flag}")
        else:
            print("  Tidak ada red flag.")

        # tren historis (DLL)
        print(f"\n  TREN RISIKO HISTORIS")
        print("  " + "-" * 40)
        tren_cr = self.navigasi.perubahan("current_ratio")
        for tahun, nilai, arah in tren_cr:
            print(f"  {tahun} | CR: {nilai:.2f}x  ({arah})")

        # window 3 tahun (CLL)
        print(f"\n  WINDOW 3 TAHUN TERAKHIR")
        print("  " + "-" * 40)
        for tahun, skor_t in self.rotasi.window(3):
            sk = skor_t.get("skor_total", 0)
            z  = skor_t.get("altman_z", 0)
            print(f"  {tahun} | Skor: {sk}  | Altman Z: {z:.2f}")

        print()

    # ──────────────────────────────────────────────────
    # FILE HANDLER
    # ──────────────────────────────────────────────────

    def simpan(self, format_file="txt"):
        tanggal   = datetime.today().strftime(cfg.OUTPUT_DATE_FORMAT)
        nama_file = f"{self.ticker}_risiko_{tanggal}.{format_file}"
        path      = cfg.OUTPUTS_DIR / nama_file

        if format_file == "json":
            self._simpan_json(path)
        else:
            self._simpan_txt(path)

        print(f"  Disimpan: {path}")
        self.riwayat.push(f"simpan:{path}")
        return path

    def _simpan_txt(self, path):
        total = self.dashboard.get("total", {})
        with open(path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write(f"LAPORAN ANALISIS RISIKO KEUANGAN\n")
            f.write(f"{self.data.profil.nama} ({self.ticker})\n")
            f.write(f"Tanggal : {datetime.today().strftime('%d %b %Y')}\n")
            f.write("=" * 60 + "\n\n")

            f.write("SKOR RISIKO PER KATEGORI\n")
            f.write("-" * 40 + "\n")
            for kategori, sk in self.urutkan_kategori_by_risiko():
                f.write(f"  {kategori:<25}: {sk:>3}/100\n")
            f.write(f"  {'TOTAL':<25}: "
                    f"{total.get('skor_risiko',0):>3}/100"
                    f"  [{total.get('level','-')}]\n\n")

            f.write("RED FLAGS\n")
            f.write("-" * 40 + "\n")
            if self.red_flags:
                for i, flag in enumerate(self.red_flags, 1):
                    f.write(f"  [{i}] {flag}\n")
            else:
                f.write("  Tidak ada red flag.\n")
            f.write("\n")

            # detail scoring model
            for kunci, label in [
                ("altman_z",    "ALTMAN Z-SCORE"),
                ("springate_s", "SPRINGATE S-SCORE"),
                ("beneish_m",   "BENEISH M-SCORE"),
            ]:
                detail = self.dashboard.get(kunci, {})
                if detail:
                    f.write(f"{label}\n")
                    f.write("-" * 40 + "\n")
                    for k, v in detail.items():
                        if isinstance(v, float):
                            f.write(f"  {k:<20}: {v:.4f}\n")
                        else:
                            f.write(f"  {k:<20}: {v}\n")
                    f.write("\n")

            f.write("RIWAYAT KALKULASI\n")
            f.write("-" * 40 + "\n")
            tmp = []
            while not self.riwayat.kosong():
                tmp.append(self.riwayat.pop())
            for item in reversed(tmp):
                f.write(f"  {item}\n")
                self.riwayat.push(item)

    def _simpan_json(self, path):
        # konversi dict agar JSON-serializable
        def bersihkan(obj):
            if isinstance(obj, dict):
                return {k: bersihkan(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [bersihkan(v) for v in obj]
            if isinstance(obj, (int, float, str, bool)) or obj is None:
                return obj
            return str(obj)

        output = {
            "ticker":           self.ticker,
            "nama":             self.data.profil.nama,
            "tanggal":          datetime.today().strftime(cfg.OUTPUT_DATE_FORMAT),
            "dashboard":        bersihkan(self.dashboard),
            "skor_per_kategori": self.skor_per_kategori,
            "red_flags":        self.red_flags,
            "historis":         self.hasil_per_tahun,
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
        