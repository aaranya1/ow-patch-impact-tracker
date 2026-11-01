from dotenv import load_dotenv

from patchimpact.config import ROOT

# Load .env before test modules are imported, so skipif checks on API keys see it.
load_dotenv(ROOT / ".env")
