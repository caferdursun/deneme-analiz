from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/deneme_analiz")

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text("DELETE FROM recommendations"))
    conn.commit()
    print(f"Deleted {result.rowcount} recommendations")
