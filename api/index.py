import os
import sys

# Ensure project root is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
# This app uses PostgreSQL for persistent storage on Vercel.
# Set the DATABASE_URL environment variable in Vercel project settings to your
# PostgreSQL connection string (e.g. from Neon, Supabase, or Railway):
#   postgres://user:password@host/dbname
#
# SQLite is ONLY used as a local development fallback when no DATABASE_URL is set.
# SQLite CANNOT be used on Vercel serverless — /tmp is ephemeral (data is lost
# between cold starts and different function instances).
# ─────────────────────────────────────────────────────────────────────────────
db_url = os.environ.get("DATABASE_URL", "")
if not db_url or "sqlite" in db_url:
    # Local development fallback only
    local_db = os.path.join(root_dir, "s60inventory.db")
    os.environ["DATABASE_URL"] = f"sqlite:///{local_db}"
    print("[DB] Using local SQLite for development. Set DATABASE_URL for production.")
else:
    # Fix legacy postgres:// URLs (Heroku/Neon style) → postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        os.environ["DATABASE_URL"] = db_url
    print(f"[DB] Using PostgreSQL database.")

from app.main import app
