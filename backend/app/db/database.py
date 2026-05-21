from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client: AsyncIOMotorClient | None = None

def connect_to_mongo() -> None:
    global client
    if client is None:
        client = AsyncIOMotorClient(
            settings.MONGO_URI,
            connectTimeoutMS=5000,
            serverSelectionTimeoutMS=5000,
        )
        print("Connected to MongoDB Atlas or local MongoDB")

async def close_mongo_connection() -> None:
    global client
    if client is not None:
        client.close()
        client = None


def get_database():
    if client is None:
        connect_to_mongo()
    return client[settings.MONGO_DB]


def get_collection(name: str):
    return get_database()[name]
