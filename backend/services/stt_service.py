from pathlib import Path
from typing import Any, Callable, Optional

from backend.models.enums import TranscriptionMode
from backend.services.cpu_limiter import CPULimiter
from backend.services.srt_builder import SRTBuilder, WordTimestamp


class STTService:
    """
    Serviço de transcrição de áudio usando Faster Whisper com suporte
    a timestamps em nível de palavra (word-level timestamps) e sincronização
    dinâmica de legendas SRT nos modos Normal, Dinâmico e Acelerado.
    """

    def __init__(
        self,
        cpu_limiter: Optional[CPULimiter] = None,
        model_size: str = "medium",
        model: Optional[Any] = None,
    ) -> None:
        self.cpu_limiter = cpu_limiter
        self.model_size = model_size
        self._model = model

    def _get_model(self) -> Any:
        """Carrega o modelo Whisper sob demanda caso não fornecido na inicialização."""
        if self._model is not None:
            return self._model

        try:
            from faster_whisper import WhisperModel

            threads = None
            if self.cpu_limiter is not None:
                threads = self.cpu_limiter.calculate_threads(75)

            self._model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type="int8",
                cpu_threads=threads or 4,
            )
            return self._model
        except ImportError:
            raise RuntimeError(
                "Faster Whisper não está instalado no ambiente. "
                "Instale 'faster-whisper' ou forneça uma instância de modelo mockado para o STTService."
            )

    def transcribe_audio(
        self,
        audio_path: str | Path,
        mode: TranscriptionMode = TranscriptionMode.NORMAL,
        mode_config: Optional[dict] = None,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> tuple[str, list[WordTimestamp], float]:
        """
        Transcreve um arquivo de áudio para PT-BR com timestamps por palavra:
        - Aplica restrições de CPU antes do início.
        - Executa Faster Whisper com word_timestamps=True e vad_filter=True.
        - Agrupa as palavras em blocos SRT de acordo com o modo de vídeo selecionado.
        - Retorna a tupla (conteúdo_srt, lista_de_palavras, duracao_total_segundos).
        """
        # 1. Aplicar limites de recursos de CPU
        if self.cpu_limiter is not None:
            self.cpu_limiter.apply_limits()

        if progress_callback:
            progress_callback(10.0, "Iniciando transcrição com Whisper...")

        model = self._get_model()
        resolved_audio = str(Path(audio_path).resolve())

        # 2. Executar transcrição com Faster Whisper
        segments_gen, info = model.transcribe(
            resolved_audio,
            language="pt",
            word_timestamps=True,
            vad_filter=True,
        )

        # 3. Extrair cada palavra com timestamp individual
        words: list[WordTimestamp] = []
        for segment in segments_gen:
            seg_words = getattr(segment, "words", None)
            if seg_words:
                for w in seg_words:
                    word_clean = getattr(w, "word", "").strip()
                    if word_clean:
                        words.append(
                            WordTimestamp(
                                word=word_clean,
                                start=float(getattr(w, "start", 0.0)),
                                end=float(getattr(w, "end", 0.0)),
                                probability=float(getattr(w, "probability", 1.0)),
                            )
                        )

        if progress_callback:
            progress_callback(75.0, "Processando timestamps e gerando legendas sincronizadas...")

        # 4. Calcular duração total em segundos
        duration = float(getattr(info, "duration", 0.0) or 0.0)
        if duration <= 0.0 and words:
            duration = max(w.end for w in words)

        # 5. Gerar conteúdo SRT
        min_sec = mode_config.get("min_seconds") if mode_config else None
        max_sec = mode_config.get("max_seconds") if mode_config else None

        srt_content = SRTBuilder.build_srt(
            words=words,
            mode=mode,
            min_seconds=min_sec,
            max_seconds=max_sec,
        )

        if progress_callback:
            progress_callback(100.0, "Transcrição concluída.")

        return srt_content, words, duration
