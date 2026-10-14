"""Application configuration for AI Procurement Copilot."""

from modules.category_engine import get_supported_procurement_categories

APP_NAME = "AI Procurement Copilot"
EDITION = "Portfolio Presentation Release v1.2"
BUILD = "Version 1.2 - Portfolio Presentation Release"
STATUS = "Portfolio Demonstration"

DEFAULT_FX_RATE = 83
DEFAULT_CATEGORY = "Packaging Materials"
SUPPORTED_CATEGORIES = get_supported_procurement_categories()
FUTURE_CATEGORIES = []
