"""Sequential integer ID generation for MongoDB documents."""

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

_COUNTERS = "counters"


async def next_sequence_id(db: AsyncIOMotorDatabase, name: str) -> int:
    """Return the next monotonic integer ID for a collection."""
    ids = await next_sequence_ids(db, name, 1)
    return ids[0]


async def next_sequence_ids(
    db: AsyncIOMotorDatabase,
    name: str,
    count: int,
) -> list[int]:
    """Return the next ``count`` monotonic integer IDs for a collection."""
    if count < 1:
        msg = "count must be at least 1"
        raise ValueError(msg)
    doc = await db[_COUNTERS].find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": count}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    end = int(doc["seq"])
    start = end - count + 1
    return list(range(start, end + 1))
