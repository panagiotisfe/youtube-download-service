import pytest
from app.services.service import download_youtube_audio
from pytube import YouTube
from pydub import AudioSegment


@pytest.mark.parametrize(
    "youtube_url",
    [
        "https://www.youtube.com/watch?v=VbN-YxUFITI",
        "https://www.youtube.com/watch?v=rYEDA3JcQqw",
    ],
)
def test_download_youtube_audio_success(youtube_url):
    youtube_object = YouTube(youtube_url)
    result = download_youtube_audio(youtube_object)
    assert result, AudioSegment


@pytest.mark.parametrize(
    "youtube_url",
    [
        "https://www.youtube.com/watch?v=fzXjskX-JJY",  # no sound video
    ],
)
def test_download_youtube_audio_failure(youtube_url):
    youtube_object = YouTube(youtube_url)
    result = download_youtube_audio(youtube_object)
    assert result, None
