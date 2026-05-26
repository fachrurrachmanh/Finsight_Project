'''
metode ini berasal dari benjamin graham
File ini dipakai untuk:
-menentukan saham murah atau mahal
-menghitung nilai wajar saham
-mencari saham undervalued
'''
import math

class GrahamAnalyzer:
    '''
    untuk Menghitung harga wajar saham menurut Graham.
    -EPS (earnings Per Share) = laba per saham.
    -BVPS (Book Value Per Share) = nilai buku per saham.
    Kalau harga saham < Graham Number, maka saham dianggap murah.
    '''
    
    def graham_number(self, eps, bvps):
        return math.sqrt(22.5 * eps * bvps)



    '''
    Menghitung nilai intrinsik saham (nilai sebenarnya bukan harga pasar)
    -eps = laba per sahan
    -growth = pertumbuhan laba perusahaan
    Kalau harga saham di bawah intrinsic value → undervalued. sebaliknya overvalued
    '''
    
    def intrinsic_value(self, eps, growth):
        return eps * (8.5 + (2 * growth))



    '''
    Menghitung Net Current Asset Value.
    Benjamin Graham percaya kalau harga saham < NCAV. maka: saham sangat murah.
    '''
    def ncav(self, aset_lancar, total_utang, jumlah_saham):
        return (aset_lancar - total_utang) / jumlah_saham