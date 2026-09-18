from pathlib import Path
from unittest.mock import MagicMock, patch
import numpy as np
import pytest

from backend.services.tts_service import TTSService


def test_presence_passed_as_exaggeration(tmp_path):
    """Verifica se presence é repassado como exaggeration ao modelo Chatterbox."""
    mock_model = MagicMock()
    mock_model.sr = 24000
    mock_model.generate.return_value = np.zeros(2400, dtype=np.float32)

    tts = TTSService(model=mock_model)
    out_file = tmp_path / "out.mp3"
    dummy_sample = tmp_path / "sample.wav"
    dummy_sample.write_bytes(b"RIFFdummyWAVEfmt ")

    with patch.object(tts, "_export_to_mp3"):
        # 1. Valor customizado de presence
        tts.generate_speech(
            text="Frase de teste",
            voice_sample_path=dummy_sample,
            output_mp3_path=out_file,
            presence=0.85,
        )
        _, kwargs = mock_model.generate.call_args
        assert kwargs.get("exaggeration") == 0.85

        # 2. Valor padrão de presence (0.5)
        tts.generate_speech(
            text="Outra frase de teste",
            voice_sample_path=dummy_sample,
            output_mp3_path=out_file,
        )
        _, kwargs = mock_model.generate.call_args
        assert kwargs.get("exaggeration") == 0.5


def test_max_pause_silence_between_chunks(tmp_path):
    """Verifica se max_pause insere arrays de silêncio com a duração correta entre chunks."""
    mock_model = MagicMock()
    mock_model.sr = 24000
    # Cada chunk tem 1000 amostras com valor 1.0 para diferenciar do silêncio (0.0)
    mock_model.generate.return_value = np.ones(1000, dtype=np.float32)

    tts = TTSService(model=mock_model)
    out_file = tmp_path / "out.mp3"
    dummy_sample = tmp_path / "sample.wav"
    dummy_sample.write_bytes(b"RIFFdummyWAVEfmt ")

    # Cenário A: 3 chunks com max_pause = 0.2s (24000 * 0.2 = 4800 amostras de silêncio cada)
    exported_arrays = []

    def fake_export(audio_arr, sample_rate, output_path, speed=1.0, pitch=0.0):
        exported_arrays.append(audio_arr.copy())

    with patch.object(TTSService, "split_text_into_chunks", return_value=["Parte 1", "Parte 2", "Parte 3"]):
        with patch.object(tts, "_export_to_mp3", side_effect=fake_export):
            tts.generate_speech(
                text="Parte 1. Parte 2. Parte 3.",
                voice_sample_path=dummy_sample,
                output_mp3_path=out_file,
                max_pause=0.2,
            )

    assert len(exported_arrays) == 1
    combined = exported_arrays[0]
    expected_samples = (1000 * 3) + (4800 * 2)  # 3 chunks + 2 pausas de 4800
    assert len(combined) == expected_samples
    # Verifica que o primeiro chunk tem 1.0
    assert np.all(combined[0:1000] == 1.0)
    # Verifica que a primeira pausa entre 1000 e 5800 é silêncio (0.0)
    assert np.all(combined[1000:5800] == 0.0)
    # Verifica o segundo chunk
    assert np.all(combined[5800:6800] == 1.0)
    # Verifica a segunda pausa entre 6800 e 11600 é silêncio (0.0)
    assert np.all(combined[6800:11600] == 0.0)
    # Verifica o terceiro chunk
    assert np.all(combined[11600:12600] == 1.0)


def test_max_pause_zero_and_single_chunk(tmp_path):
    """Verifica que max_pause=0.0 ou texto com chunk único não adicionam silêncio extra."""
    mock_model = MagicMock()
    mock_model.sr = 24000
    mock_model.generate.return_value = np.ones(1000, dtype=np.float32)

    tts = TTSService(model=mock_model)
    out_file = tmp_path / "out.mp3"
    dummy_sample = tmp_path / "sample.wav"
    dummy_sample.write_bytes(b"RIFFdummyWAVEfmt ")

    exported_arrays = []

    def fake_export(audio_arr, sample_rate, output_path, speed=1.0, pitch=0.0):
        exported_arrays.append(audio_arr.copy())

    # Cenário B: max_pause = 0.0 com 3 chunks
    with patch.object(TTSService, "split_text_into_chunks", return_value=["Parte 1", "Parte 2", "Parte 3"]):
        with patch.object(tts, "_export_to_mp3", side_effect=fake_export):
            tts.generate_speech(
                text="Parte 1. Parte 2. Parte 3.",
                voice_sample_path=dummy_sample,
                output_mp3_path=out_file,
                max_pause=0.0,
            )
    assert len(exported_arrays[0]) == 3000

    # Cenário C: 1 único chunk com max_pause = 0.5s
    exported_arrays.clear()
    with patch.object(TTSService, "split_text_into_chunks", return_value=["Parte única"]):
        with patch.object(tts, "_export_to_mp3", side_effect=fake_export):
            tts.generate_speech(
                text="Parte única",
                voice_sample_path=dummy_sample,
                output_mp3_path=out_file,
                max_pause=0.5,
            )
    assert len(exported_arrays[0]) == 1000


def test_speed_and_pitch_ffmpeg_filters(tmp_path):
    """Verifica construção dos filtros FFmpeg (-af) para diferentes combinações de speed e pitch."""
    audio = np.zeros(24000, dtype=np.float32)
    sr = 24000
    out_file = tmp_path / "test.mp3"

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)

        # 1. Padrão: speed=1.0, pitch=0.0 -> sem filtro -af
        TTSService._export_to_mp3(audio, sr, out_file, speed=1.0, pitch=0.0)
        cmd1 = mock_run.call_args[0][0]
        assert "-af" not in cmd1

        # 2. Apenas speed=1.5, pitch=0.0 -> atempo=1.5
        TTSService._export_to_mp3(audio, sr, out_file, speed=1.5, pitch=0.0)
        cmd2 = mock_run.call_args[0][0]
        assert "-af" in cmd2
        af_idx = cmd2.index("-af")
        assert cmd2[af_idx + 1] == "atempo=1.5"

        # 3. Speed fora do intervalo [0.5, 2.0]: speed=0.4 -> encadeamento de atempo
        TTSService._export_to_mp3(audio, sr, out_file, speed=0.4, pitch=0.0)
        cmd3 = mock_run.call_args[0][0]
        assert "-af" in cmd3
        af_idx = cmd3.index("-af")
        assert cmd3[af_idx + 1] == "atempo=0.5,atempo=0.8"

        # 4. Apenas pitch=12.0 (1 oitava acima), speed=1.0:
        # pitch_scale = 2.0 ** (12/12) = 2.0
        # new_rate = 24000 * 2 = 48000
        # total_tempo = (1/2.0) * 1.0 = 0.5 -> atempo=0.5
        TTSService._export_to_mp3(audio, sr, out_file, speed=1.0, pitch=12.0)
        cmd4 = mock_run.call_args[0][0]
        assert "-af" in cmd4
        af_idx = cmd4.index("-af")
        assert cmd4[af_idx + 1] == "asetrate=48000,aresample=24000,atempo=0.5"

        # 5. Pitch=-12.0 (1 oitava abaixo), speed=1.0:
        # pitch_scale = 2.0 ** (-12/12) = 0.5
        # new_rate = 24000 * 0.5 = 12000
        # total_tempo = (1/0.5) * 1.0 = 2.0 -> atempo=2.0
        TTSService._export_to_mp3(audio, sr, out_file, speed=1.0, pitch=-12.0)
        cmd5 = mock_run.call_args[0][0]
        assert "-af" in cmd5
        af_idx = cmd5.index("-af")
        assert cmd5[af_idx + 1] == "asetrate=12000,aresample=24000,atempo=2.0"


def test_generate_speech_backward_compatibility(tmp_path):
    """Verifica que generate_speech continua funcionando sem informar os novos parâmetros."""
    mock_model = MagicMock()
    mock_model.sr = 24000
    mock_model.generate.return_value = np.zeros(2400, dtype=np.float32)

    tts = TTSService(model=mock_model)
    out_file = tmp_path / "compat.mp3"
    dummy_sample = tmp_path / "sample.wav"
    dummy_sample.write_bytes(b"RIFFdummyWAVEfmt ")

    with patch.object(tts, "_export_to_mp3") as mock_export:
        res = tts.generate_speech(
            text="Chamada retrocompatível",
            voice_sample_path=dummy_sample,
            output_mp3_path=out_file,
        )
        assert res == out_file
        # Verifica que _export_to_mp3 recebeu os valores padrão
        mock_export.assert_called_once()
        _, kwargs = mock_export.call_args
        assert kwargs.get("speed") == 1.0
        assert kwargs.get("pitch") == 0.0
