from datetime import datetime
from .financial_data import (
    BalanceSheet,
    IncomeStatement,
    CashFlow,
    MarketData,
)

# profil perusahaan
# ══════════════════════════════════════════════

class CompanyProfile:
    """Informasi identitas dan profil perusahaan."""

    def __init__(
        self,
        nama,
        ticker,
        sektor,
        sub_sektor="",
        negara="Indonesia",
        mata_uang="IDR",
        harga_pasar=0.0,
        tanggal_analisis=None,
    ):
        self.nama = nama
        self.ticker = ticker.upper().strip()
        self.sektor = sektor
        self.sub_sektor = sub_sektor
        self.negara = negara
        self.mata_uang = mata_uang
        self.harga_pasar = harga_pasar

        if tanggal_analisis is None:
            self.tanggal_analisis = datetime.today().strftime("%Y-%m-%d")
        else:
            self.tanggal_analisis = tanggal_analisis



# data perusahaan
# ══════════════════════════════════════════════

class CompanyData:
    """
    Wadah utama data perusahaan — multi-periode.
    Objek ini diteruskan ke semua modul analisis.
    """

    def __init__(
        self,
        profil,
        neraca=None,
        laba_rugi=None,
        arus_kas=None,
        data_pasar=None,
    ):
        self.profil = profil

        self.neraca = neraca if neraca is not None else []
        self.laba_rugi = laba_rugi if laba_rugi is not None else []
        self.arus_kas = arus_kas if arus_kas is not None else []
        self.data_pasar = data_pasar if data_pasar is not None else []

        # Urutkan data berdasarkan tahun ascending
        self.neraca.sort(key=lambda x: x.tahun)
        self.laba_rugi.sort(key=lambda x: x.tahun)
        self.arus_kas.sort(key=lambda x: x.tahun)
        self.data_pasar.sort(key=lambda x: x.tahun)

    # ── Helper data terbaru ──────────────────────

    def tahun_tersedia(self):
        return [b.tahun for b in self.neraca]

    def neraca_terbaru(self):
        if self.neraca:
            return self.neraca[-1]
        return None

    def laba_rugi_terbaru(self):
        if self.laba_rugi:
            return self.laba_rugi[-1]
        return None

    def arus_kas_terbaru(self):
        if self.arus_kas:
            return self.arus_kas[-1]
        return None

    def pasar_terbaru(self):
        if self.data_pasar:
            return self.data_pasar[-1]
        return None

    def jumlah_tahun(self):
        return len(self.neraca)

    def ticker(self):
        return self.profil.ticker

    def harga_pasar(self):
        return self.profil.harga_pasar

    # ── Helper data historis ──────────────────────

    def eps_historis(self):
        return [i.eps for i in self.laba_rugi]

    def pendapatan_historis(self):
        return [i.pendapatan for i in self.laba_rugi]

    def laba_bersih_historis(self):
        return [i.laba_bersih for i in self.laba_rugi]

    def fcf_historis(self):
        return [c.free_cash_flow() for c in self.arus_kas]

    def dps_historis(self):
        return [i.dps for i in self.laba_rugi]

    def current_ratio_historis(self):
        result = []

        for b in self.neraca:
            if b.total_liabilitas_lancar > 0:
                ratio = (
                    b.total_aset_lancar /
                    b.total_liabilitas_lancar
                )
                result.append(ratio)
            else:
                result.append(0.0)

        return result

    def der_historis(self):
        result = []

        for b in self.neraca:
            if b.total_ekuitas > 0:
                ratio = (
                    b.total_liabilitas /
                    b.total_ekuitas
                )
                result.append(ratio)
            else:
                result.append(0.0)

        return result

    # ── validasi ──────────────────────

    def validasi(self):
        """
        Validasi kelengkapan data.

        Return:
            (valid: bool, pesan_error: list[str])
        """

        errors = []

        if not self.neraca:
            errors.append("Data neraca tidak ditemukan.")

        if not self.laba_rugi:
            errors.append("Data laba rugi tidak ditemukan.")

        if not self.arus_kas:
            errors.append("Data arus kas tidak ditemukan.")

        if self.jumlah_tahun() < 3:
            errors.append(
                f"Data hanya {self.jumlah_tahun()} tahun. "
                "Minimal 3 tahun untuk analisis dasar."
            )

        if self.profil.harga_pasar <= 0:
            errors.append(
                "Harga pasar belum diisi."
            )

        n = self.neraca_terbaru()

        if n and n.jumlah_saham_beredar <= 0:
            errors.append(
                "Jumlah saham beredar = 0."
            )

        return (len(errors) == 0, errors)