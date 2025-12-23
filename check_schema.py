from app.core.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()

print("=" * 60)
print("DATABASE TABLES")
print("=" * 60)
print(f"Tables: {tables}\n")

for table in tables:
    print(f"\n{table.upper()} TABLE COLUMNS:")
    print("-" * 60)
    cols = inspector.get_columns(table)
    for c in cols:
        print(f"  - {c['name']}: {c['type']}")
