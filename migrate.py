#!/usr/bin/env python
"""
Database migration script - handles existing tables gracefully.
"""

import sys
from sqlalchemy import create_engine, inspect


def get_alembic_config():
    """Get alembic config."""
    try:
        from alembic.config import Config
        return Config("alembic.ini")
    except ImportError:
        print("❌ Alembic not installed. Run: pip install -r requirements.txt")
        sys.exit(1)


def run_migrations():
    """Run database migrations with error handling."""
    try:
        from app.core.config import settings
        engine = create_engine(settings.database_url)
        inspector = inspect(engine)
        
        # Check what exists
        tables = inspector.get_table_names()
        has_alembic = "alembic_version" in tables
        has_users = "users" in tables
        
        print(f"Database status: {len(tables)} tables, alembic_version={'yes' if has_alembic else 'no'}")
        
        if has_users and not has_alembic:
            print("⚠️  Tables exist but no migration history.")
            print("Marking initial migration as applied...")
            alembic_cfg = get_alembic_config()
            from alembic import command
            command.stamp(alembic_cfg, "001")
            print("✅ Initial migration stamped")
        
        # Run migrations
        alembic_cfg = get_alembic_config()
        from alembic import command
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations applied successfully")
        return True
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        print("\nTrying fallback: create tables directly...")
        try:
            from app.db.database import Base, engine
            Base.metadata.create_all(bind=engine)
            print("✅ Tables created directly")
            return True
        except Exception as e2:
            print(f"❌ Fallback failed: {e2}")
            return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "down":
        try:
            alembic_cfg = get_alembic_config()
            from alembic import command
            command.downgrade(alembic_cfg, "-1")
            print("✅ Migration rolled back")
        except Exception as e:
            print(f"❌ Rollback error: {e}")
    else:
        success = run_migrations()
        sys.exit(0 if success else 1)
