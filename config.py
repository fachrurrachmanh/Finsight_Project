# config.py

# =========================
# APP INFO
# =========================
APP_NAME = "FinSight"
VERSION = "1.0.0"

# =========================
# FILE SETTINGS
# =========================
OUTPUT_FOLDER = "outputs/"
TEMPLATE_FOLDER = "templates/"
DATABASE_NAME = "finsight.db"

# =========================
# BENJAMIN GRAHAM RULES
# =========================

# Minimum Current Ratio
MIN_CURRENT_RATIO = 2.0

# Maximum Debt to Equity
MAX_DEBT_TO_EQUITY = 1.0

# Minimum EPS Growth (10 years)
MIN_EPS_GROWTH = 0.33

# Maximum PE Ratio
MAX_PE_RATIO = 15

# Maximum PB Ratio
MAX_PB_RATIO = 1.5

# Graham Number multiplier
GRAHAM_NUMBER_FACTOR = 22.5

# Minimum Interest Coverage
MIN_INTEREST_COVERAGE = 5

# =========================
# SCORING SYSTEM
# =========================

SCORE_PASS = 10
SCORE_WARNING = 5
SCORE_FAIL = 0

# =========================
# RISK LEVEL
# =========================

LOW_RISK = "LOW"
MEDIUM_RISK = "MEDIUM"
HIGH_RISK = "HIGH"

# =========================
# REPORT SETTINGS
# =========================

EXPORT_PDF = True
EXPORT_EXCEL = True
EXPORT_JSON = True

# =========================
# CLI SETTINGS
# =========================

ENABLE_COLORS = True
SHOW_LOADING_ANIMATION = True

# =========================
# GRAHAM CRITERIA WEIGHT
# =========================

WEIGHT_VALUATION = 30
WEIGHT_FINANCIAL_HEALTH = 30
WEIGHT_EARNINGS_STABILITY = 20
WEIGHT_DIVIDEND_HISTORY = 20