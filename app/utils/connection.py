from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from .config import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Declarative Meta instance
Base = declarative_base()


# DB Dependency
def get_engine(choice: int):
    settings = get_settings()
    DATABASES = {
        1: f"mssql://{settings.SERVERNAME_1}/{settings.DBNAME_1}?trusted_connection=yes&driver={settings.DRIVER_1}",
        2: f"mssql://{settings.SERVERNAME_2}/{settings.DBNAME_2}?trusted_connection=yes&driver={settings.DRIVER_2}",
        3: f"mssql+pymssql://{settings.USERNAME_1}:{settings.PSSWD_1}@{settings.SERVERNAME_1}/{settings.DBNAME_1}",
    }

    # print(DATABASES[choice])

    if choice in DATABASES:
        engine_url = DATABASES[choice]
        logger.info(f"Connecting using: {engine_url}")
        engine = create_engine(engine_url) #, echo=True)
        # inspector = inspect(engine)
        # schema_names = inspector.get_schema_names()
        # print(schema_names)
        try:
            with engine.connect() as connection:
                logger.info(
                    f"Successfully connected to the database using engine: {engine}"
                )
                return engine
        except Exception as e:
            logger.error(f"Failed to connect to the database: {e}")
            raise
    else:
        raise ValueError(
            f"Invalid choice: {choice}. Available choices are {list(DATABASES.keys())}."
        )


async def get_session(dbNum: int):
    engine = get_engine(dbNum)

    with engine.connect() as connection:
        session = sessionmaker(bind=connection)()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
