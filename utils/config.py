import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "checkin_local.json"
DEMO_MODE = os.getenv("CHECKIN_DEMO_MODE", "true").lower() == "true"
def has_databricks_config():
    return bool(os.getenv("DATABRICKS_SERVER_HOSTNAME") and os.getenv("DATABRICKS_HTTP_PATH") and os.getenv("DATABRICKS_ACCESS_TOKEN"))
