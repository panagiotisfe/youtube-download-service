import pytest
from pydub import AudioSegment


@pytest.fixture
def audio_file_to_segment():
    return AudioSegment.from_file("tests/data/test_data.mp4")
