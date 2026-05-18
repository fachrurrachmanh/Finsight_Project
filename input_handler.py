from pathlib import Path
from rich.console import Console
import pandas as pd
from models.company import CompanyProfile, CompanyData
from models.financial_data import (
    BalanceSheet, IncomeStatement, CashFlow, MarketData
)
from typing import Optional

console = Console()

class InputHandler:
    def dari_excel(self, path: str | Path) -> Optional[CompanyData]:
    
        path = Path(path)
        if not path.exists():
            console.print(f"[red]File tidak ditemukan:[/] {path}")
            return None
 
        console.print(f"\n  Membaca file: [cyan]{path.name}[/]")
 
        try:
            xls = pd.ExcelFile(path)
            sheets = [s.strip() for s in xls.sheet_names]
 
            profil      = self._baca_profil_excel(xls, sheets)
            neraca_list = self._baca_sheet_neraca(xls, sheets)
            lr_list     = self._baca_sheet_laba_rugi(xls, sheets)
            cf_list     = self._baca_sheet_arus_kas(xls, sheets)
            mp_list     = self._baca_sheet_pasar(xls, sheets)
 
            if profil is None:
                console.print("[yellow]Sheet 'Profil' tidak ditemukan, menggunakan wizard singkat...[/]")
                profil = self._tanya_profil_singkat()
 
            data = CompanyData(
                profil=profil,
                neraca=neraca_list,
                laba_rugi=lr_list,
                arus_kas=cf_list,
                data_pasar=mp_list,
            )
 
            self._tampilkan_ringkasan_data(data)
            return data
 
        except Exception as e:
            console.print(f"[red]Error membaca Excel:[/] {e}")
            return None
 
    def input_manual(self):
        print("\n=== INPUT DATA PERUSAHAAN ===")

        #profil perusahaan
        #=========================
        nama = input("Nama perusahaan: ")
        ticker = input("Kode saham: ")
        sektor = input("Sektor: ")
        harga = float(input("Harga pasar saat ini: ") or 0)

        #jumlah tahun
        # =========================
        jumlah_tahun = int(input("Berapa tahun data? ") or 3)
        tahun_akhir = int(input("Tahun terakhir: ") or 2023)

        tahun_list = list(range(
            tahun_akhir - jumlah_tahun + 1,
            tahun_akhir + 1
        ))

        neraca_list = []
        laba_rugi_list = []
        arus_kas_list = []


        # input per tahun
        # =========================
        for tahun in tahun_list:
            print(f"\n===== TAHUN {tahun} =====")

            #neraca
            # ========
            print("\n--- Neraca ---")

            kas = float(input("Kas: ") or 0)
            piutang = float(input("Piutang: ") or 0)
            persediaan = float(input("Persediaan: ") or 0)

            total_aset = float(input("Total aset: ") or 0)
            total_liabilitas = float(input("Total liabilitas: ") or 0)
            total_ekuitas = float(input("Total ekuitas: ") or 0)

            neraca = {
                "tahun": tahun,
                "kas": kas,
                "piutang": piutang,
                "persediaan": persediaan,
                "total_aset": total_aset,
                "total_liabilitas": total_liabilitas,
                "total_ekuitas": total_ekuitas
            }

            neraca_list.append(neraca)

            #laba rugi
            #==============
            print("\n--- Laba Rugi ---")

            pendapatan = float(input("Pendapatan: ") or 0)
            hpp = float(input("HPP: ") or 0)
            laba_bersih = float(input("Laba bersih: ") or 0)

            laba_rugi = {
                "tahun": tahun,
                "pendapatan": pendapatan,
                "hpp": hpp,
                "laba_bersih": laba_bersih
            }

            laba_rugi_list.append(laba_rugi)

            #arus kas
            #==========
            print("\n--- Arus Kas ---")

            cfo = float(input("Cash Flow Operasi: ") or 0)
            capex = float(input("Capex: ") or 0)
            free_cash_flow = cfo - capex

            arus_kas = {
                "tahun": tahun,
                "cfo": cfo,
                "capex": capex,
                "fcf": free_cash_flow
            }

            arus_kas_list.append(arus_kas)

            print(f"\nData tahun {tahun} berhasil disimpan.")

        # hasil akhir
        # =========================
        data = {
            "profil": {
                "nama": nama,
                "ticker": ticker,
                "sektor": sektor,
                "harga": harga
            },
            "neraca": neraca_list,
            "laba_rugi": laba_rugi_list,
            "arus_kas": arus_kas_list
        }

        return data

