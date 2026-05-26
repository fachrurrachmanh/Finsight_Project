'''
File ini adalah mesin untuk menghitung rasio keuangan perusahaan.
digunakan untuk mengetahui:
-perusahaan sehat atau tidak
-untung atau rugi
-utangnya aman atau berbahaya
-perusahaan efisien atau tidak
'''

class RatioEngine:
    '''
    menghitung current ratio = kemampuan perusahaan membayar utang jangka pendek.
    -Aset Lancar : Harta yang cepat jadi uang. 
        cth : kas, piutang, persediaan 
    -utang lancar : utang yang harus dibayar cepat
        cth : utang usaha, utang gaju, utang pajak
    kalau > 1, maka perusahaan aman. daan sebaliknya
    '''
    
    def current_ratio(self, aset_lancar, utang_lancar):
        return aset_lancar / utang_lancar



    '''
    Mengukur seberapa besar aset perusahaan dibiayai utang.
    kalau semakin kecil, maka semakin aman. dan sebaliknya akan beresiko
    '''
    
    def debt_ratio(self, total_utang, total_aset):
        return total_utang / total_aset



    '''
    Mengukur seberapa besar keuntungan dari penjualan.
    profit margin tinggi = perusahaan efisien, karena keuntungan besar. dan sebaliknya
    '''
    
    def profit_margin(self, laba_bersih, pendapatan):
        return (laba_bersih / pendapatan) * 100