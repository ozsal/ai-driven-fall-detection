"""
Database Setup Script
Initializes the SQLite database for the Fall Detection System
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from database.sqlite_db import init_database

async def setup():
    """Initialize the database"""
    print("Setting up SQLite database...")
    try:
        await init_database()
        print("✓ Database setup completed successfully!")
        print(f"Database file location: {os.path.join(os.path.dirname(__file__), 'fall_detection.db')}")
    except Exception as e:
        print(f"✗ Error setting up database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(setup())



