import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import numpy as np
import pytest

from backend.models.enums import TranscriptionMode
from backend.services.cpu_limiter import CPULimiter
from backend.services.srt_builder import WordTimestamp
from backend.services.tts_service import TTSService
from backend.services.stt_service import STTService


# ==============================================================================
# Tests for TTSService.split_text_into_chunks
# ==============================================================================

def test_split_text_into_chunks_short_text():
    """Texto curto menor que max_chars deve retornar exatamente 1 chunk."""
    text = "Olá, este é um teste curto."
    chunks = TTSService.split_text_into_chunks(text, max_chars=250)
    assert len(chunks) == 1
    assert chunks[0] == "Olá, este é um teste curto."


def test_split_text_into_chunks_empty_text():
    """Texto vazio ou apenas espaços em branco deve retornar lista vazia."""
    assert TTSService.split_text_into_chunks("", max_chars=250) == []
    assert TTSService.split_text_into_chunks("   \n\t  ", max_chars=250) == []


def test_split_text_into_chunks_multiple_sentences():
    """Texto longo com pontuações deve ser dividido em chunks respeitando pontuação."""
    s1 = "Primeira frase explicativa sobre o projeto Voxa."
    s2 = "Segunda frase trazendo mais detalhes sobre a inteligência artificial."
    s3 = "Terceira frase concluindo o raciocínio inicial."
    s4 = "Quarta frase para preencher mais caracteres."
    s5 = "Quinta e última sentença do teste."
    text = f"{s1} {s2} {s3} {s4} {s5}"

    # Limite pequeno para forçar divisão
    chunks = TTSService.split_text_into_chunks(text, max_chars=100)
    assert len(chunks) > 1
    # Todos os chunks devem ter comprimento <= max_chars (ou próximo respeitando margem)
    for chunk in chunks:
        assert len(chunk) <= 120
        assert len(chunk.strip()) > 0
    # O texto reconstruído deve conter as palavras originais
    combined = " ".join(chunks)
    assert "Primeira frase" in combined
    assert "última sentença" in combined


def test_split_text_into_chunks_without_punctuation():
    """Texto longo sem pontuação deve ser quebrado nos limites de palavras sem quebrar palavras ao meio."""
    words = ["palavra" + str(i) for i in range(40)]
    text = " ".join(words)

    chunks = TTSService.split_text_into_chunks(text, max_chars=80)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 90
        # Nenhuma palavra deve estar cortada ao meio
        for word in chunk.split():
            assert word in words


def test_split_text_into_chunks_very_long_sentence_with_commas():
    """Sentença muito longa contendo vírgulas deve dividir preferencialmente por vírgulas."""
    text = (
        "Esta é uma frase excessivamente longa que foi escrita propositalmente sem pontos finais, "
        "mas contém várias vírgulas intermediárias bem posicionadas, permitindo uma segmentação natural, "
        "sem truncamento abrupto de termos, gerando uma experiência de fala muito mais natural."
    )
    chunks = TTSService.split_text_into_chunks(text, max_chars=120)
    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk) <= 130


def test_split_text_normalizes_whitespace():
    """Normalização deve remover quebras de linha excessivas e múltiplos espaços."""
    text = "Primeira parte com   muitos    espaços.\n\n\nSegunda parte após quebras."
    chunks = TTSService.split_text_into_chunks(text, max_chars=250)
    assert len(chunks) == 1
    assert "  " not in chunks[0]
    assert chunks[0] == "Primeira parte com muitos espaços. Segunda parte após quebras."


# ==============================================================================
# Tests for TTSService.generate_speech
# ==============================================================================

def test_tts_generate_speech_success(tmp_path):
    """Gera áudio MP3 com modelo mockado e verifica progresso e saída."""
    output_mp3 = tmp_path / "output" / "audio.mp3"
    voice_sample = tmp_path / "voice.wav"
    voice_sample.write_bytes(b"dummy_voice_data")

    cpu_limiter = MagicMock(spec=CPULimiter)
    progress_calls = []

    def on_progress(pct: float, msg: str):
        progress_calls.append((pct, msg))

    # Mock do modelo Chatterbox
    mock_model = MagicMock()
    mock_model.generate.return_value = np.zeros(24000, dtype=np.float32)
    mock_model.sample_rate = 24000

    service = TTSService(cpu_limiter=cpu_limiter, model=mock_model)
    result_path = service.generate_speech(
        text="Olá mundo! Esta é uma frase de teste.",
        voice_sample_path=voice_sample,
        output_mp3_path=output_mp3,
        progress_callback=on_progress,
    )

    # 1. Limites de CPU foram aplicados
    cpu_limiter.apply_limits.assert_called()

    # 2. Modelo foi chamado com audio_prompt_path
    mock_model.generate.assert_called()
    call_kwargs = mock_model.generate.call_args[1]
    assert "audio_prompt_path" in call_kwargs or len(mock_model.generate.call_args[0]) >= 2

    # 3. Callbacks de progresso foram executados e terminaram em 100%
    assert len(progress_calls) >= 2
    assert progress_calls[-1][0] == 100.0

    # 4. Arquivo de saída foi criado
    assert result_path == output_mp3
    assert output_mp3.exists()
    assert output_mp3.stat().st_size > 0


def test_tts_generate_speech_multiple_chunks(tmp_path):
    """Testa sintetização com múltiplos chunks e concatenação."""
    output_mp3 = tmp_path / "multi_chunk.mp3"
    voice_sample = tmp_path / "voice.wav"
    voice_sample.write_bytes(b"dummy")

    mock_model = MagicMock()
    mock_model.generate.return_value = np.zeros(12000, dtype=np.float32)
    mock_model.sample_rate = 24000

    service = TTSService(model=mock_model)

    long_text = (
        "Esta é a primeira sentença completa para o teste de múltiplos pedaços. "
        "Esta é a segunda sentença que garantirá que o texto seja quebrado em mais de um bloco. "
        "E finalmente a terceira sentença para consolidar a validação de múltiplos chunks."
    )

    with patch.object(TTSService, "split_text_into_chunks", return_value=["Parte 1.", "Parte 2.", "Parte 3."]):
        progress_reports = []
        result = service.generate_speech(
            text=long_text,
            voice_sample_path=voice_sample,
            output_mp3_path=output_mp3,
            progress_callback=lambda p, m: progress_reports.append(p),
        )

        assert mock_model.generate.call_count == 3
        assert result == output_mp3
        assert output_mp3.exists()
        assert 100.0 in progress_reports


# ==============================================================================
# Tests for STTService.transcribe_audio
# ==============================================================================

class MockWord:
    def __init__(self, word: str, start: float, end: float, probability: float = 0.95):
        self.word = word
        self.start = start
        self.end = end
        self.probability = probability


class MockSegment:
    def __init__(self, text: str, words: list[MockWord]):
        self.text = text
        self.words = words


class MockTranscriptionInfo:
    def __init__(self, duration: float = 5.5):
        self.duration = duration
        self.language = "pt"


def test_stt_transcribe_audio_normal_mode(tmp_path):
    """Testa transcrição no modo normal com Faster Whisper mockado."""
    dummy_audio = tmp_path / "audio.mp3"
    dummy_audio.write_bytes(b"fake_mp3_data")

    mock_words = [
        MockWord("Olá", 0.0, 0.4),
        MockWord("amigos", 0.5, 0.9),
        MockWord("do", 1.0, 1.2),
        MockWord("Voxa.", 1.3, 1.8),
        MockWord("Este", 2.0, 2.3),
        MockWord("é", 2.4, 2.5),
        MockWord("um", 2.6, 2.7),
        MockWord("teste.", 2.8, 3.2),
    ]
    mock_segments = [MockSegment("Olá amigos do Voxa. Este é um teste.", mock_words)]
    mock_info = MockTranscriptionInfo(duration=4.5)

    mock_whisper = MagicMock()
    mock_whisper.transcribe.return_value = (mock_segments, mock_info)

    cpu_limiter = MagicMock(spec=CPULimiter)
    progress_log = []

    service = STTService(cpu_limiter=cpu_limiter, model=mock_whisper)
    srt_content, words, duration = service.transcribe_audio(
        audio_path=dummy_audio,
        mode=TranscriptionMode.NORMAL,
        progress_callback=lambda p, m: progress_log.append((p, m)),
    )

    # 1. CPU limiter foi invocado
    cpu_limiter.apply_limits.assert_called()

    # 2. Faster Whisper chamado com argumentos adequados
    mock_whisper.transcribe.assert_called_once_with(
        str(dummy_audio),
        language="pt",
        word_timestamps=True,
        vad_filter=True,
    )

    # 3. Retorno da tupla correta
    assert len(words) == 8
    assert isinstance(words[0], WordTimestamp)
    assert words[0].word == "Olá"
    assert duration == 4.5

    # 4. Conteúdo SRT gerado
    assert "1" in srt_content
    assert "-->" in srt_content
    assert "Olá amigos do Voxa" in srt_content

    # 5. Progresso inicial e final
    assert len(progress_log) >= 2
    assert progress_log[0][0] == 10.0
    assert progress_log[-1][0] == 100.0


def test_stt_transcribe_audio_modes_and_custom_config(tmp_path):
    """Testa transcrição em modo dinâmico / acelerado e com mode_config customizado."""
    dummy_audio = tmp_path / "speech.wav"
    dummy_audio.write_bytes(b"fake_wav")

    mock_words = [
        MockWord("Palavra1", 0.0, 0.5),
        MockWord("Palavra2", 0.6, 1.2),
        MockWord("Palavra3", 1.3, 2.0),
        MockWord("Palavra4", 2.1, 2.8),
    ]
    mock_segments = [MockSegment("Texto", mock_words)]
    mock_info = MockTranscriptionInfo(duration=3.0)

    mock_whisper = MagicMock()
    mock_whisper.transcribe.return_value = (mock_segments, mock_info)

    service = STTService(model=mock_whisper)

    # Teste com mode_config customizado
    custom_config = {"min_seconds": 1.0, "max_seconds": 2.0}
    srt_content, words, duration = service.transcribe_audio(
        audio_path=dummy_audio,
        mode=TranscriptionMode.DYNAMIC,
        mode_config=custom_config,
    )

    assert len(words) == 4
    assert duration == 3.0
    assert "-->" in srt_content


def test_stt_duration_fallback_when_info_duration_zero(tmp_path):
    """Quando info.duration é 0 ou None, calcula a duração a partir do último timestamp."""
    dummy_audio = tmp_path / "audio.mp3"
    dummy_audio.write_bytes(b"data")

    mock_words = [
        MockWord("Início", 0.0, 1.0),
        MockWord("Fim", 1.5, 4.2),
    ]
    mock_whisper = MagicMock()
    mock_whisper.transcribe.return_value = ([MockSegment("Início Fim", mock_words)], MockTranscriptionInfo(duration=0.0))

    service = STTService(model=mock_whisper)
    _, _, duration = service.transcribe_audio(audio_path=dummy_audio)
    assert duration == 4.2
