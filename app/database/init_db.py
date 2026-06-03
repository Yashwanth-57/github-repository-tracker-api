from app.database.db import engine
from app.database.base import Base

from app.models.repository import Repository


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)