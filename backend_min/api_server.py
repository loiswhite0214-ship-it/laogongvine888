import os
import sys
import importlib.util
from pathlib import Path

# Resolve project backend directory (crypto-trading-dashboard)
PROJECT_DIR = Path(__file__).resolve().parents[1] / 'crypto-trading-dashboard'
API_FILE = PROJECT_DIR / 'api_server.py'

if not API_FILE.exists():
    raise RuntimeError(f"api_server.py not found at {API_FILE}")

# Ensure the backend directory is importable for its intra-module imports
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

# Dynamically import the real api_server.py and expose its Flask 'app'
spec = importlib.util.spec_from_file_location("ctd_api_server", str(API_FILE))
if spec is None or spec.loader is None:
    raise RuntimeError("Failed to load spec for api_server.py")
module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(module)  # type: ignore[assignment]

# Render/Gunicorn entrypoint
app = getattr(module, 'app')

PROXIES = None  # 如不用代理可设为 None
