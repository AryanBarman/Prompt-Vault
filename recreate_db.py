from app.core.database import engine
from sqlalchemy import text

print("=" * 60)
print("FORCE DROPPING TABLES USING SQL")
print("=" * 60)

with engine.connect() as conn:
    # Drop tables in correct order (prompts first due to foreign key)
    try:
        conn.execute(text("DROP TABLE IF EXISTS prompts CASCADE"))
        conn.commit()
        print("✓ Dropped prompts table")
    except Exception as e:
        print(f"Error dropping prompts: {e}")
    
    try:
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        conn.commit()
        print("✓ Dropped users table")
    except Exception as e:
        print(f"Error dropping users: {e}")

print("\n" + "=" * 60)
print("CREATING NEW TABLES WITH CORRECT SCHEMA")
print("=" * 60)

# Import models
from app.models.user import User
from app.models.prompt import Prompt
from app.core.database import Base

# Create all tables
Base.metadata.create_all(bind=engine)
print("✓ Created all tables")

print("\n" + "=" * 60)
print("VERIFYING NEW SCHEMA")
print("=" * 60)

from sqlalchemy import inspect

inspector = inspect(engine)

print("\n--- Users table columns ---")
cols = inspector.get_columns('users')
for c in cols:
    print(f"  {c['name']}: {c['type']}")

print("\n--- Prompts table columns ---")
cols = inspector.get_columns('prompts')
for c in cols:
    print(f"  {c['name']}: {c['type']}")

print("\n" + "=" * 60)
print("DATABASE RECREATION COMPLETE!")
print("=" * 60)
