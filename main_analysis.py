from ratio_engine import RatioEngine
from graham_analyzer import GrahamAnalyzer
from risk_analyzer import RiskAnalyzer
from comparator import Comparator
from scoring_aggregator import ScoringAggregator


# OBJECT
ratio = RatioEngine()
graham = GrahamAnalyzer()
risk = RiskAnalyzer()
compare = Comparator()
score = ScoringAggregator()


# DATA
aset_lancar = 100000
utang_lancar = 40000

total_utang = 30000
total_aset = 120000

laba_bersih = 25000
pendapatan = 150000

eps = 5
bvps = 20
growth = 10

jumlah_saham = 1000

roe_perusahaan = 18
roe_industri = 15


# =========================
# RATIO ANALYSIS
# =========================

current_ratio = ratio.current_ratio(
    aset_lancar,
    utang_lancar
)

debt_ratio = ratio.debt_ratio(
    total_utang,
    total_aset
)

profit_margin = ratio.profit_margin(
    laba_bersih,
    pendapatan
)


# =========================
# GRAHAM ANALYSIS
# =========================

graham_number = graham.graham_number(
    eps,
    bvps
)

intrinsic_value = graham.intrinsic_value(
    eps,
    growth
)

ncav = graham.ncav(
    aset_lancar,
    total_utang,
    jumlah_saham
)


# =========================
# RISK ANALYSIS
# =========================

risk_result = risk.check_risk(
    debt_ratio
)


# =========================
# COMPARISON
# =========================

comparison = compare.compare_roe(
    roe_perusahaan,
    roe_industri
)


# =========================
# FINAL SCORING
# =========================

final_score = score.final_score(
    80,
    90,
    70
)

grade = score.grade(final_score)


# =========================
# OUTPUT
# =========================

print("===== HASIL ANALISIS =====")

print("Current Ratio :", current_ratio)
print("Debt Ratio    :", debt_ratio)
print("Profit Margin :", profit_margin)

print()

print("Graham Number :", graham_number)
print("Intrinsic Val :", intrinsic_value)
print("NCAV          :", ncav)

print()

print("Risk          :", risk_result)

print()

print("Comparison    :", comparison)

print()

print("Final Score   :", final_score)
print("Grade         :", grade)