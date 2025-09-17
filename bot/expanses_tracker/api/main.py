"""Main entry point for the Telegram bot."""

import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder

from expanses_tracker.application import application_registration
from expanses_tracker.persistence import persistence_registration
from expanses_tracker.persistence.database_context.database import DatabaseFactory

logging.basicConfig(level=logging.WARNING)
logging.getLogger("telegram").setLevel(logging.INFO)
# TODO fix level to propagate into submodules too
log = logging.getLogger("expenses_tracker")
log.setLevel(logging.DEBUG)

def main():
    """Main function to start the bot."""
    # Read bot token at runtime to avoid import-time failures
    bot_token = os.environ["BOT_TOKEN"]

    # Initialize database
    log.info("Initializing database...")
    try:
        # Run DB setup
        persistence_registration()
        engine_name = DatabaseFactory.get_engine_name()
        log.info("Using database engine %s:", engine_name)
    except ValueError as e:
        log.error("Database configuration error: %s", e)
        raise

    # Initialize Telegram bot
    app = ApplicationBuilder().token(bot_token).build()
    app = application_registration(app)

    log.info("Bot initialized, starting polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
