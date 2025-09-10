#!/bin/bash

# Run alembic migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting the bot..."
exec python -m expanses_tracker_tbot.api.new
