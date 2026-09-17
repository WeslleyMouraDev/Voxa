import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable, Optional

import numpy as np
from scipy.io import wavfile

from backend.services.cpu_limiter import CPULimiter


class TTSService:
    """
    Serviço de síntese e clonagem de voz usando Chatterbox TTS (PT-BR),
    com sanitização de texto, chunking inteligente para evitar cortes,
    concatenação de áudios e exportação para MP3 com limite de CPU.
    """

    def __init__(
        self,
        cpu_limiter: Optional[CPULimiter] = None,
        model: Optional[Any] = None,
    ) -> None:
        self.cpu_limiter = cpu_limiter
        self._model = model

    def _get_model(self) -> Any:
        """Carrega sob demanda o modelo ChatterboxTTS se ainda não instanciado."""
        if self._model is not None:
            return self._model

        try:
            from chatterbox import ChatterboxTTS
            self._model = ChatterboxTTS()
            return self._model
        except ImportError:
            try:
                import chatterbox_tts  # type: ignore
                self._model = chatterbox_tts.ChatterboxTTS()
                return self._model
            except ImportError:
                raise RuntimeError(
                    "Chatterbox TTS não está instalado no ambiente. "
                    "Instale 'chatterbox-tts' ou forneça uma instância do modelo para o TTSService."
                )

    @staticmethod
    def split_text_into_chunks(text: str, max_chars: int = 250) -> list[str]:
        """
        Divide o texto em chunks menores que aproximadamente max_chars:
        - Normaliza quebras de linha e espaços repetidos.
        - Divide em sentenças pelas pontuações (. ! ? ; \\n).
        - Se uma sentença individual exceder max_chars, divide por vírgulas ou espaços.
        - Agrupa sentenças menores até o limite max_chars sem truncar palavras.
        """
        cleaned_text = re.sub(r"\s+", " ", text).strip()
        if not cleaned_text:
            return []

        if len(cleaned_text) <= max_chars:
            return [cleaned_text]

        # 1. Separar em sentenças baseado em pontuações fortes
        raw_sentences = [
            s.strip()
            for s in re.split(r"(?<=[.!?])\s+", cleaned_text)
            if s.strip()
        ]

        # 2. Subdividir sentenças muito longas (> max_chars) por vírgulas ou palavras
        atomic_parts: list[str] = []
        for sentence in raw_sentences:
            if len(sentence) <= max_chars:
                atomic_parts.append(sentence)
            else:
                # Tenta dividir por vírgula ou dois-pontos
                comma_parts = [
                    cp.strip()
                    for cp in re.split(r"(?<=[,;:])\s+", sentence)
                    if cp.strip()
                ]
                for cp in comma_parts:
                    if len(cp) <= max_chars:
                        atomic_parts.append(cp)
                    else:
                        # Divide estritamente por palavras
                        words = cp.split()
                        sub_chunk: list[str] = []
                        sub_len = 0
                        for w in words:
                            add_len = len(w) + (1 if sub_chunk else 0)
                            if sub_len + add_len > max_chars and sub_chunk:
                                atomic_parts.append(" ".join(sub_chunk))
                                sub_chunk = [w]
                                sub_len = len(w)
                            else:
                                sub_chunk.append(w)
                                sub_len += add_len
                        if sub_chunk:
                            atomic_parts.append(" ".join(sub_chunk))

        # 3. Agrupar atomic_parts até atingir aproximadamente max_chars
        chunks: list[str] = []
        current_chunk: list[str] = []
        current_len = 0

        for part in atomic_parts:
            add_len = len(part) + (1 if current_chunk else 0)
            if current_len + add_len > max_chars and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [part]
                current_len = len(part)
            else:
                current_chunk.append(part)
                current_len += add_len

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def generate_speech(
        self,
        text: str,
        voice_sample_path: str | Path,
        output_mp3_path: str | Path,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Path:
        """
        Gera narração clonando a voz informada:
        1. Aplica limites de recursos via CPULimiter.
        2. Divide o texto em blocos/chunks.
        3. Sintetiza áudio de cada bloco reportando progresso.
        4. Concatena os áudios e exporta para MP3.
        """
        # 1. Aplicar limites de CPU
        if self.cpu_limiter is not None:
            self.cpu_limiter.apply_limits()

        chunks = self.split_text_into_chunks(text)
        if not chunks:
            raise ValueError("O texto para síntese de voz não pode estar vazio.")

        if progress_callback:
            progress_callback(5.0, f"Iniciando síntese de {len(chunks)} bloco(s) de texto...")

        model = self._get_model()
        voice_str = str(Path(voice_sample_path).resolve())

        audio_chunks: list[np.ndarray] = []
        sample_rate = getattr(model, "sample_rate", 24000)

        # 2. Processar cada chunk
        total_chunks = len(chunks)
        for idx, chunk in enumerate(chunks):
            if hasattr(model, "generate"):
                out = model.generate(chunk, audio_prompt_path=voice_str)
            elif hasattr(model, "synthesize"):
                out = model.synthesize(chunk, audio_prompt_path=voice_str)
            elif callable(model):
                out = model(chunk, audio_prompt_path=voice_str)
            else:
                raise RuntimeError("Modelo TTS fornecido não possui método de geração suportado.")

            # Converte saída para numpy array 1D
            arr = self._to_numpy_audio(out)
            audio_chunks.append(arr)

            pct = 10.0 + ((idx + 1) / total_chunks) * 75.0
            if progress_callback:
                progress_callback(
                    round(pct, 1),
                    f"Sintetizando bloco {idx + 1} de {total_chunks}...",
                )

        if progress_callback:
            progress_callback(88.0, "Concatenando áudios e convertendo para MP3...")

        # 3. Concatenar áudio
        combined_audio = np.concatenate(audio_chunks) if len(audio_chunks) > 1 else audio_chunks[0]

        # 4. Salvar como MP3
        out_path = Path(output_mp3_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        self._export_to_mp3(combined_audio, sample_rate, out_path)

        if progress_callback:
            progress_callback(100.0, "Síntese e conversão para MP3 concluídas.")

        return out_path

    @staticmethod
    def _to_numpy_audio(audio_data: Any) -> np.ndarray:
        """Converte tensor PyTorch, tupla ou array numpy em array 1D float32."""
        if hasattr(audio_data, "detach"):
            arr = audio_data.detach().cpu().numpy()
        elif isinstance(audio_data, tuple):
            # Formato (sr, data) ou (data, sr)
            arr = audio_data[1] if isinstance(audio_data[0], int) else audio_data[0]
            if hasattr(arr, "detach"):
                arr = arr.detach().cpu().numpy()
        else:
            arr = np.asarray(audio_data)

        arr = np.squeeze(arr)
        if arr.dtype not in (np.float32, np.float64, np.int16, np.int32):
            arr = arr.astype(np.float32)
        return arr

    @staticmethod
    def _export_to_mp3(audio_arr: np.ndarray, sample_rate: int, output_path: Path) -> None:
        """Exporta array de áudio para arquivo MP3 usando FFmpeg com fallback para WAV/cópia."""
        # Normalização para int16
        if audio_arr.dtype in (np.float32, np.float64):
            max_val = np.max(np.abs(audio_arr))
            if max_val > 1.0:
                audio_arr = audio_arr / max_val
            int16_arr = (audio_arr * 32767).astype(np.int16)
        else:
            int16_arr = audio_arr.astype(np.int16)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            temp_wav_path = tmp_file.name

        try:
            wavfile.write(temp_wav_path, sample_rate, int16_arr)

            # Tenta converter via FFmpeg
            ffmpeg_cmd = [
                "ffmpeg",
                "-y",
                "-i",
                temp_wav_path,
                "-codec:a",
                "libmp3lame",
                "-q:a",
                "2",
                str(output_path),
            ]
            result = subprocess.run(
                ffmpeg_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Se ffmpeg não conseguiu ou não existe, grava wav direto no destino
            if result.returncode != 0 or not output_path.exists():
                with open(temp_wav_path, "rb") as f_in, open(output_path, "wb") as f_out:
                    f_out.write(f_in.read())
        except Exception:
            # Fallback direto caso subprocess falhe
            wavfile.write(str(output_path), sample_rate, int16_arr)
        finally:
            if os.path.exists(temp_wav_path):
                try:
                    os.remove(temp_wav_path)
                except Exception:
                    pass
