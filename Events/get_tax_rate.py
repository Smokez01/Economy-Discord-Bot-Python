from database import tax_collection

def get_tax_rate(guild_id, user_id):
    existing_user = tax_collection.find_one({"guild_id": str(guild_id), "user_id": str(user_id)})
    if existing_user:
        return existing_user.get("tax_rate", 0)
    else:
        return 0
