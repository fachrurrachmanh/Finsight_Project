
from pathlib import Path

#info aplikasi
NAMA_APP= "FinSight"
VERSI = "1.0.0"
DESKRIPSI_APLIKASI = "Analisis Fundamental & Value Investing — Benjamin Graham"
PENGEMBANG = "FACHRURRACHMAN HAKEEM" \
             "M. FARRAS RIZKULLAH" \
             "SALWACHIKA DERI"


#setting direktori
BASE_DIR      = Path(__file__).resolve().parent
MODULES_DIR   = BASE_DIR / "modules"
MODELS_DIR    = BASE_DIR / "models"
DATABASE_DIR  = BASE_DIR / "database"
OUTPUTS_DIR   = BASE_DIR / "outputs"
TEMPLATES_DIR = BASE_DIR / "templates"

MODULES_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True,exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
 
DB_PATH = DATABASE_DIR / "finsight.db"

#prinsip benjamin graham
#=======================
GRAHAM = {
    #graham number  
    "graham_multiplier":    22.5,
 
    #margin of Safety minimum
    "min_margin_of_safety": 0.33,
 
    #batas valuasi
    "max_pe_ratio":         15.0,   
    "max_pb_ratio":          1.5,   
    "max_pe_x_pb":          22.5,  
 
    #kekuatan neraca
    "min_current_ratio":     2.0,   
    "max_der":               1.0,   
 
    #pertumbuhan laba
    "min_eps_growth_10yr":   0.33, 
      
    #dividen
    "min_dividend_years":      20,  
    "payout_ratio_min":      0.30,
    "payout_ratio_max":      0.60,
    "min_dividend_coverage": 1.50,  
 
    #data minimum
    "min_years_data":           5,
 
    #ncav
    "ncav_discount":         0.67,
}

#graham scorecard
# =========================
BOBOT_SCORECARD = {
    "graham_number_mos":      0.25,   
    "defensive_criteria":     0.20,   
    "ncav_test":              0.10,   
    "earnings_quality":       0.15,   
    "balance_sheet_strength": 0.15,   
    "dividend_consistency":   0.10,   
    "risk_penalty":           0.05,   
}

#level risiko
# =========================
RISK_LEVEL = {
    "RENDAH":      {"max": 25,  "label": "RENDAH"},
    "SEDANG":   {"max": 50,  "label": "SEDANG"},
    "TINGGI":     {"max": 75,  "label": "TINGGI"},
    "BAHAYA": {"max": 100, "label": "BAHAYA"},
}

#sektor perusahaan
# =========================
SEKTOR = [
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

#sektor perusahaan
# =========================
SEKTOR_KEUANGAN = {"Perbankan & Keuangan"}

#rasio_keuangan
# =========================
RATIO = {
    # Likuiditas
    "current_ratio":      {"nama": "Current Ratio",         "unit": "x",    "cat": "Likuiditas"},
    "quick_ratio":        {"nama": "Quick Ratio",            "unit": "x",    "cat": "Likuiditas"},
    "cash_ratio":         {"nama": "Cash Ratio",             "unit": "x",    "cat": "Likuiditas"},
    "days_cash_on_hand":  {"nama": "Days Cash on Hand",      "unit": "hari", "cat": "Likuiditas"},
 
    # Profitabilitas
    "gross_margin":       {"nama": "Gross Profit Margin",    "unit": "%",    "cat": "Profitabilitas"},
    "net_margin":         {"nama": "Net Profit Margin",      "unit": "%",    "cat": "Profitabilitas"},
    "roe":                {"nama": "Return on Equity",       "unit": "%",    "cat": "Profitabilitas"},
    "roa":                {"nama": "Return on Assets",       "unit": "%",    "cat": "Profitabilitas"},
    "roic":               {"nama": "Return on Inv. Capital", "unit": "%",    "cat": "Profitabilitas"},
    "ebitda_margin":      {"nama": "EBITDA Margin",          "unit": "%",    "cat": "Profitabilitas"},
 
    # Solvabilitas
    "der":                {"nama": "Debt-to-Equity",         "unit": "x",    "cat": "Solvabilitas"},
    "dar":                {"nama": "Debt-to-Assets",         "unit": "x",    "cat": "Solvabilitas"},
    "interest_coverage":  {"nama": "Interest Coverage",      "unit": "x",    "cat": "Solvabilitas"},
    "net_debt_ebitda":    {"nama": "Net Debt / EBITDA",      "unit": "x",    "cat": "Solvabilitas"},
 
    # Aktivitas
    "asset_turnover":     {"nama": "Asset Turnover",         "unit": "x",    "cat": "Aktivitas"},
    "inventory_turnover": {"nama": "Inventory Turnover",     "unit": "x",    "cat": "Aktivitas"},
    "receivable_days":    {"nama": "Receivable Days",        "unit": "hari", "cat": "Aktivitas"},
    "payable_days":       {"nama": "Payable Days",           "unit": "hari", "cat": "Aktivitas"},
 
    # Pasar
    "pe_ratio":           {"nama": "P/E Ratio",              "unit": "x",    "cat": "Pasar"},
    "pb_ratio":           {"nama": "P/BV Ratio",             "unit": "x",    "cat": "Pasar"},
    "ev_ebitda":          {"nama": "EV/EBITDA",              "unit": "x",    "cat": "Pasar"},
    "dividend_yield":     {"nama": "Dividend Yield",         "unit": "%",    "cat": "Pasar"},
    "peg_ratio":          {"nama": "PEG Ratio",              "unit": "x",    "cat": "Pasar"},
 
    # Graham
    "graham_number":      {"nama": "Graham Number",          "unit": "Rp",   "cat": "Graham"},
    "ncav_per_share":     {"nama": "NCAV per Saham",         "unit": "Rp",   "cat": "Graham"},
    "margin_of_safety":   {"nama": "Margin of Safety",       "unit": "%",    "cat": "Graham"},
    "epv_per_share":      {"nama": "EPV per Saham",          "unit": "Rp",   "cat": "Graham"},
    "tangible_bv":        {"nama": "Tangible Book Value",    "unit": "Rp",   "cat": "Graham"},
}

#kolom excel 
KOLOM_EXCEL = {
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


