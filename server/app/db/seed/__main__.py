import asyncio

from app.db.seed import seed

if __name__ == "__main__":
    asyncio.run(seed())
