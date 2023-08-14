from fastapi import Depends, FastAPI, BackgroundTasks, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel
from app.db import get_session
from app.models import YoutubeMetadata, ShazamMetadata
from app.services.youtube import YoutubeMetadataTransformer
from app.services.service import handle_download_and_recognize
from sqlalchemy.future import select
from pytube import YouTube
from pytube.exceptions import PytubeError
from app.exceptions import DatabaseError
import logging

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
    try:
        youtube_object = YouTube(youtube_url)
    except PytubeError as e:
        logger.error("An error occurred while processing the YouTube URL: " + str(e))
        raise HTTPException(status_code=404, detail="Error processing the YouTube URL")

    if youtube_object.length > 10 * 60:
        raise HTTPException(
            status_code=404, detail="Please provide a smaller YouTube video"
        )

    try:
        # Check if metadata for the YouTube video already exists in the database
        existing_youtube_metadata = await session.get(
            YoutubeMetadata, youtube_object.video_id
        )
        statement = select(ShazamMetadata).where(
            ShazamMetadata.youtube_id == youtube_object.video_id
        )
        results = await session.exec(statement)
        existing_shazam_metadata = results.first()
    except DatabaseError as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

    if not existing_youtube_metadata:
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

        # Initiate background task for downloading and recognition
        background_tasks.add_task(
            handle_download_and_recognize, youtube_object, youtube_metadata, session
        )
        return youtube_metadata

    if existing_youtube_metadata and existing_shazam_metadata:
        # Return existing metadata if both YouTube and Shazam metadata exist
        return existing_youtube_metadata

    # Initiate background task for downloading and recognition using existing metadata
    background_tasks.add_task(
        handle_download_and_recognize,
        youtube_object,
        existing_youtube_metadata,
        session,
    )
    return existing_youtube_metadata
