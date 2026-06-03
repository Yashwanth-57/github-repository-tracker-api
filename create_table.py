import asyncio

from app.database.init_db import init_db


asyncio.run(init_db())