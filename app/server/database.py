import motor.motor_asyncio
from bson.objectid import ObjectId

MONGO_DETAILS = "mongodb://aia_nlp:aia_nlp@localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
user_collection = client['speaker_recognition'].get_collection("user")

def user_helper(user):
    return {
        "id": str(user["_id"]),
        "fullname": user["fullname"],
        "number_phone": user["number_phone"],
    }

# Add a new user into to the database
async def add_user(user_data):
    number_phone = await user_collection.find_one({"number_phone": user_data['number_phone']})

    if number_phone is None:
        user = await user_collection.insert_one(user_data)
        new_user = await user_collection.find_one({"_id": user.inserted_id})
        return user_helper(new_user)
    else: 
        return False

async def FindUserbyNumberPhone(user_data):
    result = await user_collection.find_one({"number_phone": user_data['number_phone']})
    return result

async def update_user(user_data):
    try:
        user_update = await user_collection.update_one({"_id": user_data['_id']}, {"$set": user_data})
        return True
    except:
        return False
    