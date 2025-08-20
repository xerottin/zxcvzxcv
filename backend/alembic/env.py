import os
from logging.config import fileConfig

from alembic import context
from db.base import Base
from dotenv import find_dotenv, load_dotenv
from models import *
from sqlalchemy import engine_from_config, pool

load_dotenv(find_dotenv())

config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name)

SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL") or os.getenv("POSTGRES_URL")
if not SYNC_DATABASE_URL:
    raise RuntimeError("SYNC_DATABASE_URL or POSTGRES_URL must be set in .env")

config.set_main_option("sqlalchemy.url", SYNC_DATABASE_URL)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
