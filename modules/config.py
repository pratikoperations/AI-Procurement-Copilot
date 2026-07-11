"""Application configuration for AI Procurement Copilot."""

from modules.category_engine import get_supported_categories

APP_NAME = "AI Procurement Copilot"
EDITION = "Portfolio Edition v1.0"
BUILD = "Build 0.9.6.1 - Executive-Readable Supplier Intelligence UX Hotfix"
STATUS = "Hotfix Validation Pending"

DEFAULT_FX_RATE = 83
DEFAULT_CATEGORY = "Packaging Procurement"
SUPPORTED_CATEGORIES = get_supported_categories()
FUTURE_CATEGORIES = ["Direct Materials", "Indirect Materials"]
