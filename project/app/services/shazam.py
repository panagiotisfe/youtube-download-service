from shazamio import Shazam
from typing import Dict
from app.exceptions import RecognizeError, DataTransformationError


class ShazamAudioRecognizer:
    """
    A class to perform audio recognition using the Shazam service.
    """

    def __init__(self, audio_path: str) -> None:
        """
        Initialize the ShazamAudioRecognizer instance.

        Args:
            audio_path (str): Path to the audio file for recognition.
        """
        self.audio_path = audio_path

    async def recognise_audio(self) -> Dict:
        """
        Recognize the audio and retrieve Shazam metadata for the recognized song.

        Returns:
            Dict: Shazam metadata for the recognized song.
        Raises:
            RecognizeError: If an error occurs during audio recognition.
        """
        try:
            shazam = Shazam()
            song = await shazam.recognize_song(self.audio_path)
            if not song:
                raise RecognizeError("No song recognized from audio.")
            return song
        except Exception as e:
            raise RecognizeError(
                f"An error occurred during audio recognition. {str(e)}"
            )


class ShazamMetadataTransformer:
    """
    A class to transform Shazam metadata into a suitable format for storage.
    """

    def __init__(self, shazam_metadata: Dict, youtube_id: str) -> None:
        """
        Initialize the ShazamMetadataTransformer instance.

        Args:
            shazam_metadata (Dict): Shazam metadata for the recognized song.
            youtube_id (str): YouTube video ID associated with the metadata.
        """
        self.shazam_metadata = shazam_metadata
        self.youtube_id = youtube_id

    def transform_data(self) -> Dict:
        """
        Transform Shazam metadata into a dictionary format suitable for storage.

        Returns:
            Dict: Transformed Shazam metadata.
        Raises:
            DataTransformationError: If an error occurs during data transformation.
        """
        try:
            response = {
                "title": self.shazam_metadata.get("track", {}).get("title", None),
                "genre": self.shazam_metadata.get("track", {})
                .get("genres", {})
                .get("primary", None),
                "youtube_id": self.youtube_id,
            }

            lyrics_section = None
            sections = self.shazam_metadata.get("track", {}).get("sections", [])

            for section in sections:
                if section.get("type") == "LYRICS":
                    lyrics_section = section

            if lyrics_section:
                response["lyrics"] = " ".join(lyrics_section.get("text", []))

            return response
        except KeyError as ke:
            raise DataTransformationError(
                f"KeyError occurred during data transformation. {str(ke)}"
            )
        except Exception as e:
            raise DataTransformationError(
                f"An error occurred during data transformation. {str(e)}"
            )
