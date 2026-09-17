from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from backend.models.enums import TranscriptionMode

STRONG_PUNCTUATION = (".", "!", "?", ";")


@dataclass
class WordTimestamp:
    word: str
    start: float
    end: float
    probability: float = 1.0


@dataclass
class SRTSegment:
    index: int
    start: float
    end: float
    text: str


MODE_DEFAULTS: dict[TranscriptionMode, tuple[float, float]] = {
    TranscriptionMode.NORMAL: (4.0, 6.0),
    TranscriptionMode.DYNAMIC: (2.0, 4.0),
    TranscriptionMode.ACCELERATED: (1.0, 2.0),
}


class SRTBuilder:
    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """Converte float de segundos em timestamp SRT no formato HH:MM:SS,mmm."""
        total_ms = max(0, int(round(seconds * 1000)))
        hours = total_ms // 3600000
        minutes = (total_ms % 3600000) // 60000
        secs = (total_ms % 60000) // 1000
        ms = total_ms % 1000
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

    @classmethod
    def build_segments(
        cls,
        words: list[WordTimestamp],
        mode: TranscriptionMode = TranscriptionMode.NORMAL,
        min_seconds: Optional[float] = None,
        max_seconds: Optional[float] = None,
    ) -> list[SRTSegment]:
        """Agrupa palavras em blocos de legendas de acordo com o modo ou limites informados."""
        if not words:
            return []

        mode_enum = TranscriptionMode(mode) if isinstance(mode, str) else mode
        default_min, default_max = MODE_DEFAULTS.get(mode_enum, (4.0, 6.0))
        min_sec = min_seconds if min_seconds is not None else default_min
        max_sec = max_seconds if max_seconds is not None else default_max

        segments: list[SRTSegment] = []
        current_words: list[WordTimestamp] = []

        def commit_segment() -> None:
            nonlocal current_words
            if not current_words:
                return
            seg_text = " ".join(w.word.strip() for w in current_words).strip()
            seg = SRTSegment(
                index=len(segments) + 1,
                start=current_words[0].start,
                end=current_words[-1].end,
                text=seg_text,
            )
            segments.append(seg)
            current_words = []

        for word in words:
            if current_words:
                prev_word = current_words[-1]
                silence = word.start - prev_word.end
                curr_duration = prev_word.end - current_words[0].start
                # Quebra por silêncio substancial se o bloco corrente já tiver duração mínima proporcional
                if silence >= 1.0 and curr_duration >= min_sec * 0.7:
                    commit_segment()

            current_words.append(word)
            duration = current_words[-1].end - current_words[0].start

            word_clean = word.word.strip()
            ends_with_strong_punct = (
                any(word_clean.endswith(p) for p in STRONG_PUNCTUATION)
                or "\n" in word.word
            )

            # Quebra por pontuação forte após min_sec ou ao atingir max_sec
            if (duration >= min_sec and ends_with_strong_punct) or (duration >= max_sec):
                commit_segment()

        commit_segment()
        return segments

    @classmethod
    def build_srt(
        cls,
        words: list[WordTimestamp],
        mode: TranscriptionMode = TranscriptionMode.NORMAL,
        min_seconds: Optional[float] = None,
        max_seconds: Optional[float] = None,
    ) -> str:
        """Gera a string no formato padrão SRT."""
        segments = cls.build_segments(
            words, mode=mode, min_seconds=min_seconds, max_seconds=max_seconds
        )
        if not segments:
            return ""

        blocks: list[str] = []
        for seg in segments:
            start_str = cls.format_timestamp(seg.start)
            end_str = cls.format_timestamp(seg.end)
            blocks.append(f"{seg.index}\n{start_str} --> {end_str}\n{seg.text}")

        return "\n\n".join(blocks) + "\n"

    @staticmethod
    def save_srt_file(srt_content: str, destination_path: Path | str) -> Path:
        """Salva a string SRT em arquivo garantindo codificação utf-8."""
        dest = Path(destination_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(srt_content, encoding="utf-8")
        return dest
