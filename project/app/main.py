import ast
import logging
from pytube import YouTube
from pytube.exceptions import PytubeError
from pydantic import BaseModel
from fastapi import Depends, FastAPI, BackgroundTasks, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db import get_session
from app.db import redis_connection
from app.models import YoutubeMetadata, ShazamMetadata
from app.services.youtube import YoutubeMetadataTransformer
from app.services.service import handle_download_and_recognize
from app.settings import settings
from app.exceptions import DatabaseError


app = FastAPI()

logger = logging.getLogger(__name__)


class YoutubeResponse(BaseModel):
    title: str
    author: str
    views: int


@app.get("/url/", response_model=YoutubeResponse)
async def youtube_url(
    youtube_url: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> YoutubeResponse:
    """
    Process a YouTube URL to extract metadata and initiate recognition.

    Args:
        youtube_url (str): The URL of the YouTube video.
        background_tasks (BackgroundTasks): Asynchronous background task manager.
        session (AsyncSession): Asynchronous database session.

    Returns:
        YoutubeResponse: The extracted YoutubeMetadata.
    """
    cache = redis_connection.get(youtube_url)
    if cache:
        return ast.literal_eval(cache.decode("utf-8"))
    try:
        youtube_object = YouTube(youtube_url)
    except PytubeError as e:
        logger.error("An error occurred while processing the YouTube URL: " + str(e))
        raise HTTPException(status_code=404, detail="Error processing the YouTube URL")

    if youtube_object.length > settings.MAX_VIDEO_LENGTH:
        raise HTTPException(
            status_code=400, detail="Please provide a smaller YouTube video"
        )

    try:
        # Check if metadata for the YouTube video already exists in the database
        youtube_metadata = await session.get(YoutubeMetadata, youtube_object.video_id)
        shazam_metadata = await session.get(ShazamMetadata, youtube_object.video_id)
    except DatabaseError as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

    if not youtube_metadata:
        # If YouTube metadata doesn't exist, transform and save it to the database
        youtube_metadata_transformer = YoutubeMetadataTransformer(youtube_object)
        youtube_metadata = YoutubeMetadata(
            **youtube_metadata_transformer.transform_data()
        )
        try:
            await youtube_metadata.save(session)
        except DatabaseError as e:
            logger.error(e)
            raise HTTPException(status_code=500, detail="An unexpected error occurred")

    if not shazam_metadata:
        background_tasks.add_task(
            handle_download_and_recognize,
            youtube_object,
            youtube_metadata,
            session,
        )

    redis_json_data = jsonable_encoder(youtube_metadata)
    redis_connection.set(youtube_url, str(redis_json_data))
    redis_connection.expire(youtube_url, settings.REDIS_TTL)
    return youtube_metadata
