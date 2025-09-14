#!/bin/bash

# Run alembic migrations
echo "Running database migrations..."
cd /app && alembic upgrade head

# Start the application
echo "Starting the bot..."
exec python -m expanses_tracker.api.main
