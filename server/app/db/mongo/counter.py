"""Sequential integer ID generation for MongoDB documents."""

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

_COUNTERS = "counters"


async def next_sequence_id(db: AsyncIOMotorDatabase, name: str) -> int:
    """Return the next monotonic integer ID for a collection."""
    doc = await db[_COUNTERS].find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(doc["seq"])
