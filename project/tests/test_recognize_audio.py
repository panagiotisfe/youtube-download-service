from app.services.service import recognize_audio


def test_recognize_audio_success(audio_file_to_segment):
    result = recognize_audio(audio_file_to_segment)
    assert result, dict
