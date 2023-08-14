from pytube import YouTube
from pydub import AudioSegment
from pytube.exceptions import PytubeError
from typing import Dict
import logging
from app.exceptions import DownloadError, YoutubeAudioNotFound, DataTransformationError

logger = logging.getLogger(__name__)


class YoutubeAudioDownloader:
    """
    A class to download and process audio from a YouTube video.
    """

    def __init__(self, youtube_object: YouTube, audio_dir: str) -> None:
        """
        Initialize the YoutubeAudioDownloader instance.

        Args:
            youtube_object (YouTube): YouTube object containing video details.
            audio_dir (str): Directory where audio will be saved.
        """
        self.youtube_object = youtube_object
        self.audio_dir = audio_dir
        self.file_path = None

    def download_audio(self) -> None:
        """
        Download audio from the YouTube video and save it to the specified directory.

        Raises:
            DownloadError: If an error occurs during audio download.
            YoutubeAudioNotFound: If no suitable audio stream is found.
        """
        try:
            stream = self.youtube_object.streams.get_audio_only()
            if not stream:
                raise YoutubeAudioNotFound
            self.file_path = stream.download(self.audio_dir)
        except PytubeError as e:
            raise DownloadError(f"An error occurred during audio download. {str(e)}")

    def trim_audio_track(self) -> None:
        """
        Trim the downloaded audio to the first 20 seconds.

        Note:
            In case of an error during trimming
            the original downloaded audio remains unchanged.
        """
        try:
            audio = AudioSegment.from_file(self.file_path, "mp4")
            audio = audio.get_sample_slice(
                start_sample=0, end_sample=(20 * audio.frame_rate)
            )
            audio.export(self.file_path, format="mp4")
        except Exception:
            # In this case, if an error occurs during trimming
            # the original downloaded audio will still be available
            pass


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
            )
