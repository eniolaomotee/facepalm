import logging
from storeapi.database import database, user_table

logger = logging.getLogger(__name__)
# when you work on a backend api you look at 3 main things a.data to be stored b. data the api is going to recieve and c.return and implement the endpoint to the user.

async def get_user(email:str):
    logger.debug("Fetching user from db", extra={"email": email})
    query = user_table.select().where(user_table.c.email == email)
    result = await database.fetch_one(query)
    if result:
        return result