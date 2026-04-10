# backend/app/logger.py
import os
import sys
from pathlib import Path
from loguru import logger as log

# Determine environment (default to development)
ENV = os.getenv("ENVIRONMENT", "development").lower()

# Log format
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

# Simple format for production (no colors)
PROD_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
    "{level: <8} | "
    "{name}:{function}:{line} | "
    "{message}"
)

# Remove default handler
log.remove()

# ------------------------------------------------------------------
# Development: Console output with colors
# ------------------------------------------------------------------
if ENV == "development":
    log.add(
        sink=sys.stdout,
        format=LOG_FORMAT,
        level="DEBUG",
        colorize=True,
    )
    log.info("🔧 Logger configured for DEVELOPMENT mode")

# ------------------------------------------------------------------
# Production: File output with rotation
# ------------------------------------------------------------------
elif ENV == "production":
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Main log file (INFO and above)
    log.add(
        sink="logs/triage.log",
        format=PROD_FORMAT,
        level="INFO",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,  # Thread-safe
    )
    
    # Error log file (ERROR and above)
    log.add(
        sink="logs/triage_errors.log",
        format=PROD_FORMAT,
        level="ERROR",
        rotation="5 MB",
        retention="90 days",
        compression="zip",
        enqueue=True,
    )
    
    # Also log to console (without colors)
    log.add(
        sink=sys.stdout,
        format=PROD_FORMAT,
        level="INFO",
        colorize=False,
    )
    
    log.info("🚀 Logger configured for PRODUCTION mode")

# ------------------------------------------------------------------
# Testing: Minimal output
# ------------------------------------------------------------------
elif ENV == "testing":
    log.add(
        sink=sys.stdout,
        format="{time:HH:mm:ss} | {level} | {message}",
        level="WARNING",
    )
    log.info("🧪 Logger configured for TESTING mode")

# ------------------------------------------------------------------
# Default fallback
# ------------------------------------------------------------------
else:
    log.add(
        sink=sys.stdout,
        format=LOG_FORMAT,
        level="INFO",
        colorize=True,
    )
    log.warning(f"⚠️  Unknown environment '{ENV}', using default logging")
