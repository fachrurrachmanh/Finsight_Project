'''
File ini tugasnya mendeteksi risiko finansial perusahaan.
'''
class RiskAnalyzer:
    '''
    Mengecek tingkat risiko perusahaan.
    '''
    def check_risk(self, debt_ratio):

        if debt_ratio > 0.7:
            return "RISIKO TINGGI"

        elif debt_ratio > 0.5:
            return "RISIKO SEDANG"

        else:
            return "RISIKO RENDAH"