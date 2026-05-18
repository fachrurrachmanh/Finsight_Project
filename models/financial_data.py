# neraca  (Balance Sheet)
# ══════════════════════════════════════════════

class BalanceSheet:
    """Neraca keuangan satu periode."""

    def __init__(
        self,
        tahun,
        kas_setara_kas=0.0,
        piutang_usaha=0.0,
        persediaan=0.0,
        aset_lancar_lain=0.0,
        total_aset_lancar=0.0,
        aset_tetap_neto=0.0,
        goodwill=0.0,
        aset_tidak_berwujud=0.0,
        aset_tidak_lancar_lain=0.0,
        total_aset_tidak_lancar=0.0,
        total_aset=0.0,
        utang_usaha=0.0,
        utang_jangka_pendek=0.0,
        liabilitas_lancar_lain=0.0,
        total_liabilitas_lancar=0.0,
        utang_jangka_panjang=0.0,
        liabilitas_tidak_lancar_lain=0.0,
        total_liabilitas_tidak_lancar=0.0,
        total_liabilitas=0.0,
        modal_disetor=0.0,
        laba_ditahan=0.0,
        ekuitas_lain=0.0,
        total_ekuitas=0.0,
        jumlah_saham_beredar=0.0,
    ):
        self.tahun = tahun

        # Aset Lancar
        self.kas_setara_kas = kas_setara_kas
        self.piutang_usaha = piutang_usaha
        self.persediaan = persediaan
        self.aset_lancar_lain = aset_lancar_lain
        self.total_aset_lancar = total_aset_lancar

        # Aset Tidak Lancar
        self.aset_tetap_neto = aset_tetap_neto
        self.goodwill = goodwill
        self.aset_tidak_berwujud = aset_tidak_berwujud
        self.aset_tidak_lancar_lain = aset_tidak_lancar_lain
        self.total_aset_tidak_lancar = total_aset_tidak_lancar

        self.total_aset = total_aset

        # Liabilitas Lancar
        self.utang_usaha = utang_usaha
        self.utang_jangka_pendek = utang_jangka_pendek
        self.liabilitas_lancar_lain = liabilitas_lancar_lain
        self.total_liabilitas_lancar = total_liabilitas_lancar

        # Liabilitas Tidak Lancar
        self.utang_jangka_panjang = utang_jangka_panjang
        self.liabilitas_tidak_lancar_lain = liabilitas_tidak_lancar_lain
        self.total_liabilitas_tidak_lancar = total_liabilitas_tidak_lancar

        self.total_liabilitas = total_liabilitas

        # Ekuitas
        self.modal_disetor = modal_disetor
        self.laba_ditahan = laba_ditahan
        self.ekuitas_lain = ekuitas_lain
        self.total_ekuitas = total_ekuitas

        self.jumlah_saham_beredar = jumlah_saham_beredar

    # ── Fungsi turunan ──────────────────────────

    def working_capital(self):
        return self.total_aset_lancar - self.total_liabilitas_lancar

    def tangible_book_value(self):
        return self.total_ekuitas - self.goodwill - self.aset_tidak_berwujud

    def ncav(self):
        return self.total_aset_lancar - self.total_liabilitas

    def nnwc(self):
        return (
            self.kas_setara_kas * 1.00
            + self.piutang_usaha * 0.75
            + self.persediaan * 0.50
            - self.total_liabilitas
        )

    def net_debt(self):
        total_utang = self.utang_jangka_pendek + self.utang_jangka_panjang
        return total_utang - self.kas_setara_kas

    def ncav_per_saham(self):
        if self.jumlah_saham_beredar <= 0:
            return 0.0
        return self.ncav() / self.jumlah_saham_beredar

    def book_value_per_saham(self):
        if self.jumlah_saham_beredar <= 0:
            return 0.0
        return self.total_ekuitas / self.jumlah_saham_beredar

    def tangible_bv_per_saham(self):
        if self.jumlah_saham_beredar <= 0:
            return 0.0
        return self.tangible_book_value() / self.jumlah_saham_beredar

# laba rugi  (Income Statement)
# ══════════════════════════════════════════════

class IncomeStatement:
    """Laporan laba rugi satu periode."""

    def __init__(
        self,
        tahun,
        pendapatan=0.0,
        harga_pokok_penjualan=0.0,
        laba_kotor=0.0,
        beban_operasional=0.0,
        beban_penyusutan=0.0,
        ebit=0.0,
        ebitda=0.0,
        beban_bunga=0.0,
        pendapatan_lain=0.0,
        laba_sebelum_pajak=0.0,
        pajak=0.0,
        laba_bersih=0.0,
        eps=0.0,
        dps=0.0,
        jumlah_saham_beredar=0.0,
    ):
        self.tahun = tahun
        self.pendapatan = pendapatan
        self.harga_pokok_penjualan = harga_pokok_penjualan
        self.laba_kotor = laba_kotor
        self.beban_operasional = beban_operasional
        self.beban_penyusutan = beban_penyusutan
        self.ebit = ebit
        self.ebitda = ebitda
        self.beban_bunga = beban_bunga
        self.pendapatan_lain = pendapatan_lain
        self.laba_sebelum_pajak = laba_sebelum_pajak
        self.pajak = pajak
        self.laba_bersih = laba_bersih

        self.eps = eps
        self.dps = dps
        self.jumlah_saham_beredar = jumlah_saham_beredar

    # ── Fungsi turunan ──────────────────────────

    def gross_margin(self):
        if self.pendapatan <= 0:
            return 0.0
        return self.laba_kotor / self.pendapatan

    def net_margin(self):
        if self.pendapatan <= 0:
            return 0.0
        return self.laba_bersih / self.pendapatan

    def ebitda_margin(self):
        if self.pendapatan <= 0:
            return 0.0
        return self.ebitda / self.pendapatan

    def ebit_margin(self):
        if self.pendapatan <= 0:
            return 0.0
        return self.ebit / self.pendapatan

    def tax_rate(self):
        if self.laba_sebelum_pajak <= 0:
            return 0.0
        return self.pajak / self.laba_sebelum_pajak

    def payout_ratio(self):
        if self.eps <= 0:
            return 0.0
        return self.dps / self.eps

    def dividend_coverage(self):
        if self.dps <= 0:
            return 0.0
        return self.eps / self.dps


# ══════════════════════════════════════════════
# ARUS KAS  (Cash Flow Statement)
# ══════════════════════════════════════════════

class CashFlow:
    """Laporan arus kas satu periode."""

    def __init__(
        self,
        tahun,
        arus_kas_operasi=0.0,
        depresiasi_amortisasi=0.0,
        perubahan_modal_kerja=0.0,
        capex=0.0,
        akuisisi=0.0,
        arus_kas_investasi=0.0,
        penerbitan_utang=0.0,
        pembayaran_utang=0.0,
        penerbitan_saham=0.0,
        dividen_dibayar=0.0,
        buyback_saham=0.0,
        arus_kas_pendanaan=0.0,
        perubahan_kas=0.0,
    ):
        self.tahun = tahun

        self.arus_kas_operasi = arus_kas_operasi
        self.depresiasi_amortisasi = depresiasi_amortisasi
        self.perubahan_modal_kerja = perubahan_modal_kerja

        self.capex = capex
        self.akuisisi = akuisisi
        self.arus_kas_investasi = arus_kas_investasi

        self.penerbitan_utang = penerbitan_utang
        self.pembayaran_utang = pembayaran_utang
        self.penerbitan_saham = penerbitan_saham
        self.dividen_dibayar = dividen_dibayar
        self.buyback_saham = buyback_saham
        self.arus_kas_pendanaan = arus_kas_pendanaan

        self.perubahan_kas = perubahan_kas

    # ── Fungsi turunan ──────────────────────────

    def free_cash_flow(self):
        return self.arus_kas_operasi - abs(self.capex)

    def capex_to_cfo(self):
        if self.arus_kas_operasi <= 0:
            return 0.0
        return abs(self.capex) / self.arus_kas_operasi


# ══════════════════════════════════════════════
# DATA PASAR  (Market Data)
# ══════════════════════════════════════════════

class MarketData:
    """Data pasar per periode."""

    def __init__(
        self,
        tahun,
        harga_saham=0.0,
        market_cap=0.0,
        enterprise_value=0.0,
    ):
        self.tahun = tahun
        self.harga_saham = harga_saham
        self.market_cap = market_cap
        self.enterprise_value = enterprise_value

    # ── Fungsi turunan ──────────────────────────

    def ev_valid(self):
        return self.enterprise_value > 0