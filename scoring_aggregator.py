'''
untuk menyatukan semuanya menjadi nilai akhir.
'''
class ScoringAggregator:
    def final_score(self, ratio_score, graham_score, risk_score):

        total = (
            ratio_score +
            graham_score +
            risk_score
        ) / 3

        return total


    '''
    untuk Mengubah score menjadi grade.
    '''
    def grade(self, score):

        if score >= 80:
            return "A"

        elif score >= 70:
            return "B"

        elif score >= 60:
            return "C"

        else:
            return "D"