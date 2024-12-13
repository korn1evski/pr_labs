#!/bin/sh
set -e

# Wait for PostgreSQL to be ready
# Replace `postgres_lab_2` and `5432` if you changed your service name or port
echo "Waiting for PostgreSQL to start..."
until pg_isready -h postgres_lab_2 -U postgres; do
  echo "Postgres not ready, retrying in 2s..."
  sleep 2
done

echo "Postgres is ready, creating tables..."
# Run create_tables via a Python one-liner or directly if you have a management command
python -c "from database import create_tables; create_tables()"

echo "Starting Flask..."
exec flask run --host=0.0.0.0
