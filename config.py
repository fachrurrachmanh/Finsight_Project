"""
config.py  —  Konfigurasi Global FinSight CLI
==============================================
Semua konstanta, acuan, bobot, dan path ada di sini.
Seluruh modul cukup: import config as cfg
"""

from pathlib import Path

# ──────────────────────────────────────────────────────
# INFORMASI APLIKASI
# ──────────────────────────────────────────────────────
APP_NAME        = "FinSight CLI"
APP_VERSION     = "1.0.0"
APP_DESCRIPTION = "Analisis Fundamental & Value Investing — Benjamin Graham"
APP_AUTHOR      = "FinSight"

# ──────────────────────────────────────────────────────
# DIREKTORI
# ──────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).resolve().parent
MODULES_DIR   = BASE_DIR / "modules"
MODELS_DIR    = BASE_DIR / "models"
DATABASE_DIR  = BASE_DIR / "database"
OUTPUTS_DIR   = BASE_DIR / "outputs"
TEMPLATES_DIR = BASE_DIR / "templates"

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATABASE_DIR / "finsight.db"

# ──────────────────────────────────────────────────────
# ACUAN BENJAMIN GRAHAM
# ──────────────────────────────────────────────────────
GRAHAM = {
    # Graham Number  =  sqrt(22.5 * EPS * BV)
    "graham_multiplier":    22.5,

    # Margin of Safety minimum (Graham: 33%)
    "min_margin_of_safety": 0.33,

    # Batas valuasi
    "max_pe_ratio":         15.0,   
    "max_pb_ratio":          1.5,   
    "max_pe_x_pb":          22.5,   

    # Kekuatan neraca
    "min_current_ratio":     2.0,   
    "max_der":               1.0,   

    # Pertumbuhan laba
    "min_eps_growth_10yr":   0.33,  

    # Dividen
    "min_dividend_years":      20,  
    "payout_ratio_min":      0.30,
    "payout_ratio_max":      0.60,
    "min_dividend_coverage": 1.50,  

    # Data minimum
    "min_years_data":           5,

    # NCAV - beli jika harga < 67% NCAV
    "ncav_discount":         0.67,
}

# ──────────────────────────────────────────────────────
# ACUAN RISIKO KEUANGAN
# ──────────────────────────────────────────────────────
RISK = {
    # Altman Z-Score
    "altman_safe":            2.99,   
    "altman_grey":            1.81,   
                                      

    # Beneish M-Score  (manipulasi laba)
    "beneish_threshold":     -1.78,   

    # Springate S-Score  (kebangkrutan)
    "springate_threshold":   0.862,   

    # Solvabilitas
    "min_interest_coverage":  3.0,    
    "max_net_debt_ebitda":    3.0,    

    # Accrual Ratio  =  (Net Income - FCF) / Total Aset
    "accrual_ratio_warning":  0.05,   
    "accrual_ratio_danger":   0.10,   

    # Likuiditas
    "min_cash_ratio":         0.20,
    "min_days_cash":            30,   

    # Volatilitas EPS  (CV = StdDev / Mean)
    "eps_cv_stable":          0.15,  
    "eps_cv_moderate":        0.30,   
}

# ──────────────────────────────────────────────────────
# BOBOT GRAHAM SCORECARD  (total = 100%)
# ──────────────────────────────────────────────────────
SCORECARD_WEIGHTS = {
    "graham_number_mos":      0.25,   
    "defensive_criteria":     0.20,   
    "ncav_test":              0.10,   
    "earnings_quality":       0.15,   
    "balance_sheet_strength": 0.15,   
    "dividend_consistency":   0.10,   
    "risk_penalty":           0.05,   
}

# ──────────────────────────────────────────────────────
# SISTEM PENILAIAN
# ──────────────────────────────────────────────────────
GRADE = {
    "A": {"min": 90, "label": "STRONG BUY",   "color": "bright_green"},
    "B": {"min": 75, "label": "BUY",           "color": "green"},
    "C": {"min": 60, "label": "HOLD / WATCH",  "color": "yellow"},
    "D": {"min": 45, "label": "AVOID",         "color": "red"},
    "F": {"min":  0, "label": "SELL / DANGER", "color": "bright_red"},
}

# Rekomendasi berdasarkan Margin of Safety
RECOMMENDATION = {
    "strong_buy": {"min_mos":  0.40, "label": "STRONG BUY   — beli agresif"},
    "buy":        {"min_mos":  0.33, "label": "BUY          — beli bertahap"},
    "accumulate": {"min_mos":  0.20, "label": "ACCUMULATE   — cicil perlahan"},
    "watch":      {"min_mos":  0.10, "label": "WATCH        — pantau terus"},
    "avoid":      {"min_mos":  0.00, "label": "AVOID        — belum layak beli"},
    "overvalued": {"min_mos":  None, "label": "OVERVALUED   — jauhi"},
}

# ──────────────────────────────────────────────────────
# LEVEL RISIKO
# ──────────────────────────────────────────────────────
RISK_LEVEL = {
    "LOW":      {"max": 25,  "label": "RENDAH", "color": "green"},
    "MEDIUM":   {"max": 50,  "label": "SEDANG", "color": "yellow"},
    "HIGH":     {"max": 75,  "label": "TINGGI", "color": "red"},
    "CRITICAL": {"max": 100, "label": "KRITIS", "color": "bright_red"},
}

# ──────────────────────────────────────────────────────
# SEKTOR PERUSAHAAN
# ──────────────────────────────────────────────────────
SECTORS = [
    "Perbankan & Keuangan",
    "Properti & Real Estate",
    "Energi & Pertambangan",
    "Konsumer Primer",
    "Konsumer Sekunder",
    "Industri & Manufaktur",
    "Teknologi & Telekomunikasi",
    "Infrastruktur",
    "Kesehatan",
    "Transportasi & Logistik",
    "Agrikultur & Perkebunan",
    "Lainnya",
]

# Sektor keuangan: threshold DER berbeda
FINANCIAL_SECTORS = {"Perbankan & Keuangan"}

# ──────────────────────────────────────────────────────
# FORMAT OUTPUT
# ──────────────────────────────────────────────────────
OUTPUT_FORMATS      = ["pdf", "xlsx", "json", "txt"]
OUTPUT_DATE_FORMAT  = "%Y-%m-%d"
OUTPUT_FILE_PATTERN = "{ticker}_{type}_{date}.{ext}"
# contoh: TLKM_analysis_2025-01-15.pdf

# ──────────────────────────────────────────────────────
# TAMPILAN CLI
# ──────────────────────────────────────────────────────
CLI = {
    "table_width":     80,
    "separator":       "─",
    "box_style":       "rounded",
    "date_format":     "%d %b %Y",
    "float_decimal":    2,
    "percent_decimal":  1,
}

# ──────────────────────────────────────────────────────
# METADATA RASIO
# ──────────────────────────────────────────────────────
RATIO_META = {
    # Likuiditas
    "current_ratio":      {"name": "Current Ratio",         "unit": "x",    "cat": "Likuiditas"},
    "quick_ratio":        {"name": "Quick Ratio",            "unit": "x",    "cat": "Likuiditas"},
    "cash_ratio":         {"name": "Cash Ratio",             "unit": "x",    "cat": "Likuiditas"},
    "days_cash_on_hand":  {"name": "Days Cash on Hand",      "unit": "hari", "cat": "Likuiditas"},

    # Profitabilitas
    "gross_margin":       {"name": "Gross Profit Margin",    "unit": "%",    "cat": "Profitabilitas"},
    "net_margin":         {"name": "Net Profit Margin",      "unit": "%",    "cat": "Profitabilitas"},
    "roe":                {"name": "Return on Equity",       "unit": "%",    "cat": "Profitabilitas"},
    "roa":                {"name": "Return on Assets",       "unit": "%",    "cat": "Profitabilitas"},
    "roic":               {"name": "Return on Inv. Capital", "unit": "%",    "cat": "Profitabilitas"},
    "ebitda_margin":      {"name": "EBITDA Margin",          "unit": "%",    "cat": "Profitabilitas"},

    # Solvabilitas
    "der":                {"name": "Debt-to-Equity",         "unit": "x",    "cat": "Solvabilitas"},
    "dar":                {"name": "Debt-to-Assets",         "unit": "x",    "cat": "Solvabilitas"},
    "interest_coverage":  {"name": "Interest Coverage",      "unit": "x",    "cat": "Solvabilitas"},
    "net_debt_ebitda":    {"name": "Net Debt / EBITDA",      "unit": "x",    "cat": "Solvabilitas"},

    # Aktivitas
    "asset_turnover":     {"name": "Asset Turnover",         "unit": "x",    "cat": "Aktivitas"},
    "inventory_turnover": {"name": "Inventory Turnover",     "unit": "x",    "cat": "Aktivitas"},
    "receivable_days":    {"name": "Receivable Days",        "unit": "hari", "cat": "Aktivitas"},
    "payable_days":       {"name": "Payable Days",           "unit": "hari", "cat": "Aktivitas"},

    # Pasar
    "pe_ratio":           {"name": "P/E Ratio",              "unit": "x",    "cat": "Pasar"},
    "pb_ratio":           {"name": "P/BV Ratio",             "unit": "x",    "cat": "Pasar"},
    "ev_ebitda":          {"name": "EV/EBITDA",              "unit": "x",    "cat": "Pasar"},
    "dividend_yield":     {"name": "Dividend Yield",         "unit": "%",    "cat": "Pasar"},
    "peg_ratio":          {"name": "PEG Ratio",              "unit": "x",    "cat": "Pasar"},

    # Graham
    "graham_number":      {"name": "Graham Number",          "unit": "Rp",   "cat": "Graham"},
    "ncav_per_share":     {"name": "NCAV per Saham",         "unit": "Rp",   "cat": "Graham"},
    "margin_of_safety":   {"name": "Margin of Safety",       "unit": "%",    "cat": "Graham"},
    "epv_per_share":      {"name": "EPV per Saham",          "unit": "Rp",   "cat": "Graham"},
    "tangible_bv":        {"name": "Tangible Book Value",    "unit": "Rp",   "cat": "Graham"},
}

# ──────────────────────────────────────────────────────
# KOLOM EXCEL TEMPLATE
# ──────────────────────────────────────────────────────
EXCEL_COLUMNS = {
    "balance_sheet": {
        "Tahun":                    "tahun",
        "Kas & Setara Kas":         "kas_setara_kas",
        "Piutang Usaha":            "piutang_usaha",
        "Persediaan":               "persediaan",
        "Aset Lancar Lain":         "aset_lancar_lain",
        "Total Aset Lancar":        "total_aset_lancar",
        "Aset Tetap (Neto)":        "aset_tetap_neto",
        "Goodwill":                 "goodwill",
        "Aset Tidak Berwujud":      "aset_tidak_berwujud",
        "Total Aset Tidak Lancar":  "total_aset_tidak_lancar",
        "Total Aset":               "total_aset",
        "Utang Usaha":              "utang_usaha",
        "Utang Jangka Pendek":      "utang_jangka_pendek",
        "Liabilitas Lancar Lain":   "liabilitas_lancar_lain",
        "Total Liabilitas Lancar":  "total_liabilitas_lancar",
        "Utang Jangka Panjang":     "utang_jangka_panjang",
        "Liabilitas Tidak Lancar":  "liabilitas_tidak_lancar_lain",
        "Total Liabilitas":         "total_liabilitas",
        "Modal Disetor":            "modal_disetor",
        "Laba Ditahan":             "laba_ditahan",
        "Total Ekuitas":            "total_ekuitas",
        "Jumlah Saham Beredar":     "jumlah_saham_beredar",
    },
    "income_statement": {
        "Tahun":                    "tahun",
        "Pendapatan":               "pendapatan",
        "HPP":                      "harga_pokok_penjualan",
        "Laba Kotor":               "laba_kotor",
        "Beban Operasional":        "beban_operasional",
        "EBIT":                     "ebit",
        "EBITDA":                   "ebitda",
        "Beban Bunga":              "beban_bunga",
        "Laba Sebelum Pajak":       "laba_sebelum_pajak",
        "Pajak":                    "pajak",
        "Laba Bersih":              "laba_bersih",
        "EPS":                      "eps",
        "DPS":                      "dps",
    },
    "cash_flow": {
        "Tahun":                    "tahun",
        "Arus Kas Operasi":         "arus_kas_operasi",
        "Capex":                    "capex",
        "Free Cash Flow":           "free_cash_flow",
        "Arus Kas Investasi":       "arus_kas_investasi",
        "Arus Kas Pendanaan":       "arus_kas_pendanaan",
        "Perubahan Kas":            "perubahan_kas",
    },
    "market_data": {
        "Tahun":                    "tahun",
        "Harga Saham":              "harga_saham",
        "Market Cap":               "market_cap",
        "Enterprise Value":         "enterprise_value",
    },
}
