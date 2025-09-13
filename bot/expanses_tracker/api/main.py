import os, logging
from telegram import Update
from telegram.ext import ApplicationBuilder

from expanses_tracker.application import application_registration
from expanses_tracker.persistence import persistence_registration
from expanses_tracker.persistence.database_context.database import DatabaseFactory

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger(__name__)

def main():
    # Read bot token at runtime to avoid import-time failures
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    
    # Initialize database
    log.info("Initializing database...")
    try:
        # Run DB setup
        persistence_registration()
        engine_name = DatabaseFactory.get_engine_name()
        log.info(f"Using database engine: {engine_name}")
    except ValueError as e:
        log.error(f"Database configuration error: {e}")
        raise
    
    # Initialize Telegram bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app = application_registration(app)
    
    log.info("Bot initialized, starting polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
