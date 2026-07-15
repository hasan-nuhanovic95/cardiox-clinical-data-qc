# from pathlib import Path
# PROJECT_ROOT = Path(__file__).resolve().parent
# RAW_DIR = PROJECT_ROOT / "data" / "raw"
# OUTPUT_DIR = PROJECT_ROOT / "outputs"
# LOG_DIR = PROJECT_ROOT / "logs"

# OUTPUT_DIR.mkdir(exist_ok=True)
# LOG_DIR.mkdir(exist_ok=True)

# OUTPUT_FILE = OUTPUT_DIR / "review_workbook.xlsx"
# LOG_FILE = LOG_DIR / "pipeline.log"

from pathlib import Path


# Ovdje je razlika u odnosu na kod iznad
PROJECT_ROOT = Path(__file__).resolve().parents[1]
# jer je config.py sada u src/, pa je root projekta jedan nivo iznad src.

RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
LOG_DIR = PROJECT_ROOT / "logs"

OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "review_workbook.xlsx"
LOG_FILE = LOG_DIR / "pipeline.log"
