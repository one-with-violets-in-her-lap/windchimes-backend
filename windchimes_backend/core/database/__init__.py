import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from windchimes_backend.config import app_config


logger = logging.getLogger(__name__)


class Database:
    def __init__(self, url: str, echo=False) -> None:
        self._engine = create_async_engine(
            url,
            echo=echo,
        )

        logger.info("initialized database engine with url: %s", url)

        self.create_session = async_sessionmaker(
            bind=self._engine, autoflush=False, autocommit=False, expire_on_commit=False
        )

    async def close(self):
        logger.info("closing sqlalchemy engine")
        await self._engine.dispose()

    async def get_session(self):
        async with self.create_session() as session:
            yield session


database = Database(url=str(app_config.database.url))
