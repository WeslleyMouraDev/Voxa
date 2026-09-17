import pytest
from pathlib import Path

from backend.models.enums import TranscriptionMode
from backend.services.srt_builder import (
    SRTBuilder,
    SRTSegment,
    WordTimestamp,
)


def test_word_timestamp_and_srt_segment_instantiation():
    wt = WordTimestamp(word="teste", start=0.0, end=0.5)
    assert wt.word == "teste"
    assert wt.start == 0.0
    assert wt.end == 0.5
    assert wt.probability == 1.0

    seg = SRTSegment(index=1, start=0.0, end=2.5, text="teste de legenda")
    assert seg.index == 1
    assert seg.start == 0.0
    assert seg.end == 2.5
    assert seg.text == "teste de legenda"


def test_format_timestamp():
    assert SRTBuilder.format_timestamp(0.0) == "00:00:00,000"
    assert SRTBuilder.format_timestamp(65.432) == "00:01:05,432"
    assert SRTBuilder.format_timestamp(3661.05) == "01:01:01,050"
    assert SRTBuilder.format_timestamp(0.005) == "00:00:00,005"
    assert SRTBuilder.format_timestamp(3599.999) == "00:59:59,999"


def test_empty_words():
    segments = SRTBuilder.build_segments([])
    assert segments == []

    srt = SRTBuilder.build_srt([])
    assert srt == ""


def test_normal_mode_defaults_and_max_duration():
    # Palavras a cada 0.5s sem pontuação
    # 0.0 - 0.5, 0.5 - 1.0, ..., 7.0 - 7.5
    words = [
        WordTimestamp(word=f"palavra{i}", start=i * 0.5, end=(i + 1) * 0.5)
        for i in range(15)  # 0.0 até 7.5s
    ]

    segments = SRTBuilder.build_segments(words, mode=TranscriptionMode.NORMAL)
    assert len(segments) >= 2
    # No modo normal: min 4.0, max 6.0
    # O primeiro segmento deve quebrar quando atingir max_seconds (6.0s)
    first_seg = segments[0]
    duration = first_seg.end - first_seg.start
    assert duration <= 6.0
    assert duration >= 4.0
    assert first_seg.index == 1
    assert segments[1].index == 2


def test_dynamic_mode():
    # Dinâmico: min 2.0s, max 4.0s
    words = [
        WordTimestamp(word=f"palavra{i}", start=i * 0.5, end=(i + 1) * 0.5)
        for i in range(16)  # 0.0 até 8.0s
    ]

    segments = SRTBuilder.build_segments(words, mode=TranscriptionMode.DYNAMIC)
    for seg in segments:
        duration = seg.end - seg.start
        # O último segmento pode ser menor que min_seconds se acabar as palavras
        if seg != segments[-1]:
            assert 2.0 <= duration <= 4.0
        else:
            assert duration <= 4.0


def test_accelerated_mode():
    # Acelerado: min 1.0s, max 2.0s
    words = [
        WordTimestamp(word=f"rapido{i}", start=i * 0.2, end=(i + 1) * 0.2)
        for i in range(25)  # 0.0 até 5.0s
    ]

    segments = SRTBuilder.build_segments(words, mode=TranscriptionMode.ACCELERATED)
    for seg in segments:
        duration = seg.end - seg.start
        if seg != segments[-1]:
            assert 1.0 <= duration <= 2.0
        else:
            assert duration <= 2.0


def test_punctuation_split_after_min_seconds():
    # No modo NORMAL (min=4.0s):
    # Se uma palavra aos 4.2s termina com ponto '.', deve quebrar o segmento
    words = [
        WordTimestamp(word="Olá,", start=0.0, end=0.8),
        WordTimestamp(word="amigos.", start=0.8, end=1.5),  # 1.5s < 4.0s -> não quebra
        WordTimestamp(word="Bem-vindos", start=1.5, end=2.5),
        WordTimestamp(word="ao", start=2.5, end=3.0),
        WordTimestamp(word="canal!", start=3.0, end=4.2),  # 4.2s >= 4.0s e termina com '!' -> quebra!
        WordTimestamp(word="Hoje", start=4.2, end=5.0),
        WordTimestamp(word="falaremos", start=5.0, end=6.0),
        WordTimestamp(word="de", start=6.0, end=6.5),
        WordTimestamp(word="IA.", start=6.5, end=7.2),
    ]

    segments = SRTBuilder.build_segments(words, mode=TranscriptionMode.NORMAL)
    assert len(segments) == 2
    assert segments[0].text == "Olá, amigos. Bem-vindos ao canal!"
    assert segments[0].start == 0.0
    assert segments[0].end == 4.2
    assert segments[1].text == "Hoje falaremos de IA."
    assert segments[1].start == 4.2
    assert segments[1].end == 7.2


def test_silence_break():
    # Quebra por silêncio: word.start - prev_word.end >= 1.0s
    # E o segmento atual tem pelo menos min_seconds * 0.7
    # No modo NORMAL (min=4.0s), 4.0 * 0.7 = 2.8s
    words = [
        WordTimestamp(word="Primeira", start=0.0, end=1.0),
        WordTimestamp(word="frase", start=1.0, end=3.0),  # Duração atual = 3.0s (>= 2.8s)
        # Silêncio de 1.2s entre 3.0s e 4.2s
        WordTimestamp(word="Segunda", start=4.2, end=5.0),
        WordTimestamp(word="frase", start=5.0, end=6.0),
    ]

    segments = SRTBuilder.build_segments(words, mode=TranscriptionMode.NORMAL)
    assert len(segments) == 2
    assert segments[0].text == "Primeira frase"
    assert segments[0].end == 3.0
    assert segments[1].text == "Segunda frase"
    assert segments[1].start == 4.2


def test_silence_ignored_if_segment_too_short():
    # Silêncio >= 1.0s, mas segmento tem menos de min_seconds * 0.7 (ex: 1.0s < 2.8s)
    words = [
        WordTimestamp(word="Oi", start=0.0, end=1.0),  # Duração = 1.0s (< 2.8s)
        # Silêncio de 1.1s
        WordTimestamp(word="tudo", start=2.1, end=3.0),
        WordTimestamp(word="bem?", start=3.0, end=4.5),
    ]

    segments = SRTBuilder.build_segments(words, mode=TranscriptionMode.NORMAL)
    # Não deve ter quebrado no silêncio porque 1.0s < 2.8s
    assert len(segments) == 1
    assert segments[0].text == "Oi tudo bem?"


def test_custom_min_and_max_seconds():
    words = [
        WordTimestamp(word=f"palavra{i}", start=i * 0.5, end=(i + 1) * 0.5)
        for i in range(10)  # 0.0 a 5.0s
    ]
    # Limites customizados: min 1.5s, max 3.0s
    segments = SRTBuilder.build_segments(words, min_seconds=1.5, max_seconds=3.0)
    assert len(segments) >= 2
    assert segments[0].end - segments[0].start == 3.0


def test_build_srt_string_format():
    words = [
        WordTimestamp(word="Olá,", start=0.0, end=1.0),
        WordTimestamp(word="mundo.", start=1.0, end=4.5),
        WordTimestamp(word="Nova", start=4.5, end=6.0),
        WordTimestamp(word="linha.", start=6.0, end=9.0),
    ]

    srt_content = SRTBuilder.build_srt(words, mode=TranscriptionMode.NORMAL)
    expected = (
        "1\n"
        "00:00:00,000 --> 00:00:04,500\n"
        "Olá, mundo.\n\n"
        "2\n"
        "00:00:04,500 --> 00:00:09,000\n"
        "Nova linha."
    )
    assert srt_content.strip() == expected.strip()


def test_save_srt_file(tmp_path: Path):
    content = (
        "1\n"
        "00:00:00,000 --> 00:00:02,000\n"
        "Legenda com acentuação: Olá você!\n"
    )
    dest = tmp_path / "subtitles" / "output.srt"
    saved_path = SRTBuilder.save_srt_file(content, dest)

    assert saved_path.exists()
    assert saved_path == dest
    saved_text = saved_path.read_text(encoding="utf-8")
    assert saved_text == content
