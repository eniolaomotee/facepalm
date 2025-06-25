import logging
import httpx
from storeapi.config import config

logger = logging.getLogger(__name__)

class APIResponseError(Exception):
    pass

async def send_email(to:str, subject:str, body:str):
    logger.debug("Sending email", extra={"to": to, "subject": subject})
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"https://api.mailgun.net/v3/{config.MAILGUN_DOMAIN}/messages",
                auth=('api', config.MAILGUN_API_KEY),
                data={
                    "from":f"Eniola Omotee <mailgun@{config.MAILGUN_DOMAIN}>",
                    "to":[to],
                    "subject": subject,
                    "text": body
                }
            )
            response.raise_for_status()
            
            logger.debug(response.content)
            
            return response
        except httpx.HTTPStatusError as err:
            raise APIResponseError(
                f"API request failed with status code {err.response.status_code}"
            ) from err
            
async def send_user_registration_email(email:str, confirmation_link:str):
    return await send_email(
        email,
        "successfully signed up",
        (
            f"Hi {email}! You have successfully signed up for the Stores REST API."
            "Please confirm your email by clicking on the"
            f"following link: {confirmation_link}" 
        )
    )