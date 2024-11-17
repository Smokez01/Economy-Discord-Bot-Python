import pymongo

#mongodb+srv://YourUsername:<YourPassword>@YourDataBaseName.???.mongodb.net/

mongo_client = pymongo.MongoClient("mongodb+srv://Renas:1-x2-y3-z123abc@bot.ficzu1h.mongodb.net/")

mongo_db = mongo_client["datenbank"]
money_collection = mongo_db["money"]
income_collection = mongo_db["income"]
tax_collection = mongo_db["taxes"]
money_log_collection = mongo_db["moneylog"]