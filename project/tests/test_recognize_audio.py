import pytest
from app.services.service import recognize_audio


@pytest.mark.asyncio
async def test_recognize_audio_success(audio_file_to_segment):
    result = await recognize_audio(audio_file_to_segment)
    assert result, dict
