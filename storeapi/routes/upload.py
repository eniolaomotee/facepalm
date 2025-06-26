import logging
import tempfile
import aiofiles
from fastapi import APIRouter,HTTPException, UploadFile, status
from storeapi.libs.b2 import b2_upload_file

logger = logging.getLogger(__name__)

router = APIRouter()

# File flow
# client -> server(tempfile) -> B2 -> delete tempfile

# client split up file into chunks of 1MB
# client sends up chunks 1 at a time (async)
# client sends the last chunk, all  chunks are put together in the temp file and upload to b2 and tempfile is deleted.


CHUNK_SIZE = 1024 * 1024

@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_file(file:UploadFile):
    try:
        with tempfile.NamedTemporaryFile() as temp_file:
            filename = temp_file.name
            logger.info("Saving uploaded file temporarily to {filename} ")
            async with aiofiles.open(filename, "wb") as f:
                while chunk := await file.read(CHUNK_SIZE):
                    await f.write(chunk)
            file_url = b2_upload_file(local_file=filename, file_name=file.filename)
            # user.profile_picture_url = file_url
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error uploading the file"
        )
        
    return {"detail": f"Successfully uploaded {file.filename}", "file_url":file_url}