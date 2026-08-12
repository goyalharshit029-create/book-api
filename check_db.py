from app.database import engine
from sqlalchemy import text

tables = ["books", "users", "contacts", "issued_books"]

with engine.connect() as connection:
    for table in tables:
        result = connection.execute(
            text(f"SELECT COUNT(*) FROM {table}")
        )
        count = result.scalar()

        print(f"{table}: {count} records")