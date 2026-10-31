import os
import sys
import shutil

# Ensure project root is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Handle SQLite on Vercel's serverless environment (/tmp is writable)
if not os.environ.get("DATABASE_URL") or "sqlite" in os.environ.get("DATABASE_URL", ""):
    tmp_db = "/tmp/s60inventory.db"
    src_db = os.path.join(root_dir, "s60inventory.db")
    if not os.path.exists(tmp_db) and os.path.exists(src_db):
        try:
            shutil.copy2(src_db, tmp_db)
        except Exception as e:
            print(f"[Vercel Init] SQLite copy notice: {e}")
    if os.path.exists(tmp_db):
        os.environ["DATABASE_URL"] = f"sqlite:///{tmp_db}"

from app.main import app
