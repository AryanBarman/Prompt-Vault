from app.core.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
cols = inspector.get_columns('users')
print('Users table columns:')
for c in cols:
    print(f'  - {c["name"]} ({c["type"]})')

print('\nPrompts table columns:')
cols = inspector.get_columns('prompts')
for c in cols:
    print(f'  - {c["name"]} ({c["type"]})')
