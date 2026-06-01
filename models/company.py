"""
models/company.py
==================
Class profil dan wadah data perusahaan multi-periode.
"""

from datetime import datetime
from sort_utils import merge_sort

class CompanyProfile:
    def __init__(self, nama="", ticker="", sektor="Lainnya",
                 sub_sektor="", negara="Indonesia", mata_uang="IDR",
                 harga_pasar=0.0, tanggal_analisis=None):

        self.nama             = nama
        self.ticker           = ticker.upper().strip()
        self.sektor           = sektor
        self.sub_sektor       = sub_sektor
        self.negara           = negara
        self.mata_uang        = mata_uang
        self.harga_pasar      = harga_pasar
        self.tanggal_analisis = tanggal_analisis or datetime.today().strftime("%Y-%m-%d")

class CompanyData:
    def __init__(self, profil, neraca=None, laba_rugi=None,
                 arus_kas=None, data_pasar=None):

        self.profil     = profil
        self.neraca     = merge_sort(neraca     or [], key=lambda x: x.tahun)
        self.laba_rugi  = merge_sort(laba_rugi  or [], key=lambda x: x.tahun)
        self.arus_kas   = merge_sort(arus_kas   or [], key=lambda x: x.tahun)
        self.data_pasar = merge_sort(data_pasar or [], key=lambda x: x.tahun)

    def tahun_tersedia(self):
        return [b.tahun for b in self.neraca]

    def jumlah_tahun(self):
        return len(self.neraca)

    def neraca_terbaru(self):
        return self.neraca[-1] if self.neraca else None

    def laba_rugi_terbaru(self):
        return self.laba_rugi[-1] if self.laba_rugi else None

    def arus_kas_terbaru(self):
        return self.arus_kas[-1] if self.arus_kas else None

    def pasar_terbaru(self):
        return self.data_pasar[-1] if self.data_pasar else None

    def eps_historis(self):
        return [i.eps for i in self.laba_rugi]

    def pendapatan_historis(self):
        return [i.pendapatan for i in self.laba_rugi]

    def fcf_historis(self):
        return [c.free_cash_flow() for c in self.arus_kas]

    def dps_historis(self):
        return [i.dps for i in self.laba_rugi]

    def validasi(self):
        """Return (valid: bool, errors: list[str])"""
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
            errors.append("Harga pasar belum diisi — valuasi tidak dapat dihitung.")

        n = self.neraca_terbaru()
        if n and n.jumlah_saham_beredar <= 0:
            errors.append("Jumlah saham beredar = 0.")

        return (len(errors) == 0, errors)