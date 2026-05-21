from app.db.database import get_collection

class UserService:
    @staticmethod
    async def get_user_by_id(user_id: str):
        collection = get_collection("users")
        return await collection.find_one({"_id": user_id})
