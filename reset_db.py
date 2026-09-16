#!/usr/bin/env python
"""
Reset database script - removes existing database file.
Use with caution!
"""

import os
import sys
from app.core.config import settings


def reset_database():
    """Remove the database file to start fresh."""
    db_path = settings.database_url.replace("sqlite:///", "")

    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Removed database file: {db_path}")
            return True
        except Exception as e:
            print(f"Error removing database: {e}")
            return False
    else:
        print(f"Database file not found: {db_path}")
        return True


if __name__ == "__main__":
    print("This will delete all data in the database!")
    response = input("Are you sure? (yes/no): ")

    if response.lower() in ["yes", "y"]:
        if reset_database():
            print("Database reset complete. Run 'python migrate.py' to recreate tables.")
    else:
        print("Cancelled.")
