import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Obtener la configuración de Alembic
config = context.config

# Configurar la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Configurar logging si hay un archivo de configuración presente
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Importar modelos para que Alembic detecte cambios automáticamente
from models import Base  # Asegúrate de importar correctamente

# Definir la metadata de los modelos para generar las migraciones
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecutar migraciones en modo offline.

    Configura el contexto con solo una URL sin crear un Engine.
    """
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
    """Ejecutar migraciones en modo online.

    Crea un Engine y asocia una conexión con el contexto.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# Determinar si se ejecuta en modo offline u online
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
