import asyncio, os, certifi
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
async def test():
    uri = os.getenv("MONGO_URI")
    client = AsyncIOMotorClient(uri, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
    try:
        await client.admin.command('ping')
        print("Connected successfully")
    except Exception as e:
        print(f"Error: {e}")
    client.close()

asyncio.run(test())
