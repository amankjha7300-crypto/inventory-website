import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.session import get_db, Base, engine
from app.models.all_models import Admin, AuditLog
from app.database.seed import seed_database
from app.schemas.schemas import ApiResponse
from app.api.deps import require_super_admin
from app.core.config import settings

router = APIRouter(prefix="/system", tags=["System Management"])

@router.get("/db-status")
def db_status(db: Session = Depends(get_db)):
    """
    Public diagnostic endpoint to verify database connection, type, and status.
    """
    try:
        # Run test query
        db.execute(text("SELECT 1"))
        
        # Ensure schema tables exist (safe to call repeatedly)
        try:
            Base.metadata.create_all(bind=engine)
        except Exception:
            pass
            
        admin_count = db.query(Admin).count()
        db_url_env = os.environ.get("DATABASE_URL", "")
        is_postgres = "postgres" in settings.clean_database_url or "postgres" in db_url_env
        
        return {
            "status": "connected",
            "database_type": "PostgreSQL (Cloud - Persistent)" if is_postgres else "SQLite (Temporary)",
            "is_persistent_cloud": is_postgres,
            "registered_admins": admin_count,
            "message": "Connected to cloud PostgreSQL! Accounts and changes persist across all users and devices." if is_postgres else "Running on SQLite fallback. Add DATABASE_URL to Vercel Settings to activate permanent cloud PostgreSQL."
        }
    except Exception as e:
        return {
            "status": "error",
            "error_detail": str(e),
            "message": "Could not connect to database. Check DATABASE_URL format or database credentials."
        }

@router.post("/reset-clean", response_model=ApiResponse)
def reset_clean(
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_super_admin)
):
    """
    Clears all dummy/test data and resets database to a completely clean state:
    0 students, 0 events, 0 distributions.
    """
    seed_database(force=True, include_demo=False)
    return ApiResponse(
        success=True,
        message="Database reset to clean slate. All dummy data cleared. Ready for your actual student and event entries."
    )
