import logging
from pytube import YouTube
from pytube.exceptions import PytubeError
from pydub import AudioSegment
from typing import Dict
from io import BytesIO
from app.exceptions import DownloadError, YoutubeAudioNotFound, DataTransformationError

logger = logging.getLogger(__name__)


class YoutubeAudioDownloader:
    """
    A class to download and process audio from a YouTube video.
    """

    def __init__(self, youtube_object: YouTube, buffer: BytesIO) -> None:
        """
        Initialize an instance of the AudioDownloader class.

        Args:
            youtube_object (YouTube): A YouTube object representing the video.
            buffer (BytesIO): A BytesIO buffer to store the downloaded audio.
            audio_segment: Initially set to None.
            It will hold the audio data segment once downloaded.
        """
        self.youtube_object = youtube_object
        self.buffer = buffer
        self.audio_segment = None

    def download_audio(self) -> None:
        """
        Download the audio from a YouTube video using the
        provided YouTube object and saves it to the buffer.

        Raises:
            DownloadError: If an error occurs during audio download.
            YoutubeAudioNotFound: If no suitable audio stream is found.
        """
        try:
            if stream := self.youtube_object.streams.get_audio_only():
                stream.stream_to_buffer(self.buffer)
            else:
                raise YoutubeAudioNotFound
        except PytubeError as e:
            raise DownloadError(
                f"An error occurred during audio download. {str(e)}"
            ) from e

    def convert_to_audio_segment(self) -> AudioSegment:
        """
        Convert the downloaded audio into an AudioSegment
        trimming it to the first 20 seconds.

        Returns:
            AudioSegment: An AudioSegment object containing the trimmed audio.

        Raises:
            Exception: If an error occurs during the conversion or trimming.
        """
        try:
            self.buffer.seek(0)
            self.audio_segment = AudioSegment.from_file(self.buffer, "mp4")
            self.audio_segment = self.audio_segment.get_sample_slice(
                start_sample=0, end_sample=(20 * self.audio_segment.frame_rate)
            )
        except Exception as e:
            logger.error(e)


class YoutubeMetadataTransformer:
    """
    A class to transform YouTube video details into suitable metadata format.
    """

    def __init__(self, youtube_object: YouTube) -> None:
        """
        Initialize the YoutubeMetadataTransformer instance.

        Args:
            youtube_object (YouTube): YouTube object containing video details.
        """
        self.youtube_object = youtube_object

    def transform_data(self) -> Dict:
        """
        Transform YouTube video details into a dictionary
        format suitable for metadata storage.

        Returns:
            Dict: Transformed metadata.
        Raises:
            DataTransformationError:
            If an error occurs during data transformation.
        """
        try:
            return {
                "id": self.youtube_object.video_id,
                "title": self.youtube_object.title,
                "author": self.youtube_object.author,
                "views": self.youtube_object.views,
            }
        except Exception as e:
            raise DataTransformationError(
                f"An error occurred during data transformation. {str(e)}"
            ) from e
