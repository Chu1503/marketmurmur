#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Checking seed data..."
python -c "
import sys
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.models.company import Company
db = SessionLocal()
count = db.query(Company).count()
db.close()
print(f'Companies in DB: {count}')
"

echo "Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000