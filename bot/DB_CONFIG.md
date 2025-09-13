# Expense Tracker Database Configuration

This project uses SQLAlchemy ORM to support multiple database backends:

- SQLite (for development)
- PostgreSQL (recommended for production)
- MariaDB (alternative option)

## Configuration

The database connection is configured via a single environment variable:

```
# Required: Database connection URL (SQLAlchemy format)
DATABASE_URL=dialect://username:password@host:port/database
```

## Database Connection URL Examples

### SQLite

```
# SQLite with a file path
DATABASE_URL=sqlite:///expenses.db

# SQLite with an absolute path
DATABASE_URL=sqlite:////absolute/path/to/expenses.db

# SQLite in-memory database (for testing)
DATABASE_URL=sqlite:///:memory:
```

### PostgreSQL

```
# Basic PostgreSQL connection
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/expenses

# PostgreSQL with SSL mode
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/expenses?sslmode=require
```

### MariaDB/MySQL

```
# MariaDB connection
DATABASE_URL=mysql+mysqldb://root:password@localhost:3306/expenses

# With character set and collation
DATABASE_URL=mysql+mysqldb://root:password@localhost:3306/expenses?charset=utf8mb4
```

## Docker Compose Configuration

When using Docker Compose, configure the database connection in your `.env` file. You can use the provided `.env.docker` as a template:

```bash
# Copy the docker environment template
cp .env.docker .env
# Edit the .env file with your settings
nano .env
```

For PostgreSQL (default):
```
# PostgreSQL configuration
DATABASE_URL=postgresql://postgres:postgres@db:5432/expenses
DB_IMAGE=postgres:16-alpine
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=expenses
```

For MariaDB:
```
# MariaDB configuration
DATABASE_URL=mysql+mysqldb://root:mariadb@db:3306/expenses
DB_IMAGE=mariadb:11
MYSQL_ROOT_PASSWORD=mariadb
MYSQL_DATABASE=expenses
```

For SQLite (no external database service needed):
```
# SQLite configuration
DATABASE_URL=sqlite:///expenses.db
# Comment out DB_IMAGE to disable the database service
```

## Database Migrations

The project uses Alembic for database migrations. The `DATABASE_URL` environment variable must be set for Alembic to work properly.

```bash
# Set the DATABASE_URL environment variable first
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/expenses

# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head

# Roll back the last migration
alembic downgrade -1

# Check current migration status
alembic current
```

## Data Model

The main data model is `ExpenseModel` which represents an expense entry:
- `msg_id`: Telegram message ID
- `chat_id`: Telegram chat ID
- `user_id`: Telegram user ID
- `amount`: The expense amount
- `description`: Description of the expense
- `type`: Type of expense (need, want, goal)
- `category`: Category of expense (food, utilities, etc.)
- `date`: Date of the expense
- `chat_id`: Telegram chat ID
- `created_at`: When the record was created
- `updated_at`: When the record was last updated
- `deleted_at`: When the record has been soft deleted
