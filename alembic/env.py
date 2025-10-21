from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.engine import URL

from alembic import context
from dotenv import load_dotenv
from app.model import Base

load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


def get_url():
    user = os.environ.get("SqlAlchemyUser")
    password = os.environ.get("SqlAlchemyPassword")
    host = os.environ.get("SqlAlchemyHost", "localhost")
    port = int(os.environ.get("SqlAlchemyPort", "3306"))
    # Support both correct and legacy-typo env var names
    db = os.environ.get("SqlAlchemyDatabase")

    return URL.create(
        drivername="mysql",
        username=user,
        password=password,
        host=host,
        port=port,
        database=db,
        query={"charset": "utf8mb4"},
    )


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    if not configuration:
        configuration = {}
    if not configuration.get("sqlalchemy.url"):
        configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
