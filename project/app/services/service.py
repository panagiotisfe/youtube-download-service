from .youtube import YoutubeAudioDownloader
from .shazam import ShazamAudioRecognizer
from pydub import AudioSegment
import logging
from io import BytesIO
from app.models import ShazamMetadata
from .shazam import ShazamMetadataTransformer
from typing import Union, Dict
from app.exceptions import (
    DataTransformationError,
    DatabaseError,
    RecognizeError,
    DownloadError,
)

logger = logging.getLogger(__name__)


async def handle_download_and_recognize(
    youtube_object, youtube_metadata, session
) -> None:
    """
    Handle the process of downloading YouTube audio, recognizing it using Shazam,
    and saving the Shazam metadata.

    Args:
        youtube_object: YouTube object containing video details.
        youtube_metadata: Metadata of the YouTube video.
        session: Asynchronous database session.
    """
    try:
        youtube_audio = download_youtube_audio(youtube_object)
        logger.info(f"Downloaded youtube audio: {youtube_audio}")
        shazam_response = await recognize_audio(youtube_audio)
        await save_shazam_metadata(shazam_response, youtube_metadata, session)
    except DownloadError as e:
        logger.error(e)
    except RecognizeError as e:
        logger.error(e)
    except DataTransformationError as e:
        logger.error(e)
    except DatabaseError as e:
        logger.error(e)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")


def download_youtube_audio(youtube_object) -> AudioSegment:
    """
    Download and process audio from a YouTube video.

    Args:
        youtube_object: YouTube object containing video details.

    Returns:
        Union[YoutubeAudioDownloader, None]:
        Instance of YoutubeAudioDownloader or None if unsuccessful.
    """
    buffer = BytesIO()
    youtube_audio = YoutubeAudioDownloader(youtube_object, buffer)
    youtube_audio.download_audio()
    youtube_audio.convert_to_audio_segment()
    return youtube_audio.audio_segment


async def recognize_audio(audio_segment) -> Union[Dict, None]:
    """
    Recognize audio using Shazam.

    Args:
        audio_segment: Path to the audio file for recognition.

    Returns:
        Union[Dict, None]:
        Shazam recognition response as a dictionary or None if unsuccessful.
    """
    shazam_audio = ShazamAudioRecognizer(audio_segment)
    shazam_response = await shazam_audio.recognize_audio()
    return shazam_response


async def save_shazam_metadata(shazam_response, youtube_metadata, session) -> None:
    """
    Save Shazam metadata to the database.

    Args:
        shazam_response: Shazam recognition response.
        youtube_metadata: Metadata of the corresponding YouTube video.
        session: Asynchronous database session.
    """
    shazam_metadata_transformer = ShazamMetadataTransformer(
        shazam_response, youtube_metadata.id
    )
    transformed_shazam_response = shazam_metadata_transformer.transform_data()
    shazam_metadata = ShazamMetadata(**transformed_shazam_response)
    await shazam_metadata.save(session)
