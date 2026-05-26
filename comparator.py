'''
File ini tugasnya membandingkan performa perusahaan.
'''
class Comparator:
    '''
    ROE = Return on Equity
    ROE Mengukur seberapa efektif perusahaan menghasilkan laba dari modal pemilik.
    '''
    def compare_roe(self, roe_perusahaan, roe_industri):

        if roe_perusahaan > roe_industri:
            return "ROE perusahaan lebih baik"

        else:
            return "ROE industri lebih baik"