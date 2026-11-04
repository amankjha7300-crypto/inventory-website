import os
import sys
import shutil

# Ensure project root is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE CONFIGURATION & SERVERLESS RESILIENCE
# ─────────────────────────────────────────────────────────────────────────────
db_url = os.environ.get("DATABASE_URL", "").strip()

# Strip any accidental wrapping quotes user might have pasted
if (db_url.startswith('"') and db_url.endswith('"')) or (db_url.startswith("'") and db_url.endswith("'")):
    db_url = db_url[1:-1].strip()

# Strip accidental 'psql ' prefix if user copied from Neon CLI snippet
if db_url.startswith("psql "):
    db_url = db_url[5:].strip()
    if (db_url.startswith('"') and db_url.endswith('"')) or (db_url.startswith("'") and db_url.endswith("'")):
        db_url = db_url[1:-1].strip()

if db_url and ("postgres" in db_url):
    # Convert legacy postgres:// to postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    # Ensure SSL is enabled for cloud Postgres (Neon, Supabase, etc.)
    if "sslmode=" not in db_url and "localhost" not in db_url:
        separator = "&" if "?" in db_url else "?"
        db_url = f"{db_url}{separator}sslmode=require"
    
    os.environ["DATABASE_URL"] = db_url
    print(f"[DB] Initialized with Cloud PostgreSQL ({db_url.split('@')[-1] if '@' in db_url else 'configured'}).")
else:
    # Fallback to SQLite (Local Dev or Vercel before DATABASE_URL is set)
    # CRITICAL: On Vercel / Lambda, root_dir is READ-ONLY. We MUST use /tmp so
    # database writes (signup, password reset, updates) do not crash with
    # 'sqlite3.OperationalError: attempt to write a readonly database'.
    src_db = os.path.join(root_dir, "s60inventory.db")
    tmp_dir = "/tmp"
    
    if os.path.exists(tmp_dir) and os.access(tmp_dir, os.W_OK):
        tmp_db = os.path.join(tmp_dir, "s60inventory.db")
        if not os.path.exists(tmp_db) and os.path.exists(src_db):
            try:
                shutil.copy2(src_db, tmp_db)
            except Exception as e:
                print(f"[DB Fallback] Notice copying to /tmp: {e}")
        os.environ["DATABASE_URL"] = f"sqlite:///{tmp_db}"
        print("[DB] Warning: Using /tmp SQLite fallback. Configure DATABASE_URL in Vercel for permanent storage.")
    else:
        os.environ["DATABASE_URL"] = f"sqlite:///{src_db}"
        print("[DB] Using local SQLite.")

from app.main import app
