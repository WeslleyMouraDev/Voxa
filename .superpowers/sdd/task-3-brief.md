# Task 3 Brief: Controles de Geração no Motor TTS (Ritmo, Pausa, Tom, Presença)

## Objetivo
Atualizar o `TTSService` em `backend/services/tts_service.py` para suportar os controles de geração de voz (`speed`, `max_pause`, `pitch`, `presence`), integrando com o Chatterbox (`exaggeration`) e FFmpeg (`atempo`, `asetrate`, concatenação com pausas).

## Arquivos a Modificar / Criar
- Modificar: `backend/services/tts_service.py`
- Criar: `tests/test_voice_controls.py`
- Relatório: `d:\Projetos\Voxa\.superpowers\sdd\task-3-report.md`

## Requisitos Técnicos

### 1. `backend/services/tts_service.py`
- Atualizar assinatura de `generate_speech`:
  ```python
  def generate_speech(
      self,
      text: str,
      voice_sample_path: str | Path,
      output_mp3_path: str | Path,
      progress_callback: Optional[Callable[[float, str], None]] = None,
      speed: float = 1.0,
      max_pause: float = 0.3,
      pitch: float = 0.0,
      presence: float = 0.5,
  ) -> Path:
  ```
- **Presença (`presence`)**:
  - Na chamada de `gen_method(chunk, **kwargs)`:
    Se `"exaggeration"` estiver na assinatura de `generate` ou se `has_kwargs` for True:
    Passar `kwargs["exaggeration"] = float(presence)`.
- **Pausa máxima (`max_pause`)**:
  - Ao concatenar a lista `audio_chunks`:
    Se houver mais de 1 chunk e `max_pause > 0`:
    Criar silêncio: `pause_samples = int(sample_rate * max_pause)`.
    `silence_array = np.zeros(pause_samples, dtype=np.float32)`.
    Intercalar `silence_array` entre os chunks de áudio na concatenação final.
- **Ritmo (`speed`) e Tom (`pitch`)**:
  - Atualizar `_export_to_mp3`:
    ```python
    @staticmethod
    def _export_to_mp3(
        audio_arr: np.ndarray,
        sample_rate: int,
        output_path: Path,
        speed: float = 1.0,
        pitch: float = 0.0,
    ) -> None:
    ```
  - Construção do filtro de áudio FFmpeg (`-af`):
    - Se `pitch != 0.0`:
      - Razão de escala semitons: `pitch_scale = 2.0 ** (pitch / 12.0)`.
      - Efeito: alterar taxa de amostragem e compensar tempo:
        `new_rate = int(sample_rate * pitch_scale)`
        O tempo de compensação do pitch é `1.0 / pitch_scale`.
        O tempo total a aplicar no `atempo` é `total_tempo = (1.0 / pitch_scale) * speed`.
        Para lidar com `atempo` em cadeias (pois cada filtro `atempo` suporta de 0.5 a 2.0):
        Montar filtros `atempo` encadeados se `total_tempo < 0.5` ou `total_tempo > 2.0`.
        Filtro completo:
        `f"asetrate={new_rate},aresample={sample_rate},{atempo_chain}"`
    - Se `pitch == 0.0` e `speed != 1.0`:
      - Montar apenas cadeia de filtros `atempo={speed}` (dividindo em múltiplos se fora de [0.5, 2.0]).
    - Se houver filtros de áudio, incluir no comando FFmpeg:
      `["ffmpeg", "-y", "-i", temp_wav_path, "-af", audio_filter, "-codec:a", "libmp3lame", "-q:a", "2", str(output_path)]`
    - Se não houver filtros (`speed == 1.0` e `pitch == 0.0`), comando permanece idêntico ao atual sem `-af`.
    - Manter o fallback seguro caso FFmpeg falhe ou não consiga processar.

### 2. Testes em `tests/test_voice_controls.py`
- Teste de `presence`: verificar que `exaggeration` é repassado com o valor de `presence`.
- Teste de `max_pause`: verificar tamanho do array resultante com e sem pausa entre chunks.
- Teste de `speed` e `pitch`: verificar construção dos argumentos de filtro do FFmpeg com `unittest.mock.patch("subprocess.run")`.
- Teste de retrocompatibilidade: verificar que chamar `generate_speech` com apenas os argumentos antigos continua funcionando perfeitamente com valores padrão.

### 3. Ciclo TDD
- Criar `tests/test_voice_controls.py`.
- Rodar `.venv\Scripts\python.exe -m pytest tests/test_voice_controls.py -v` (confirmar falha).
- Implementar em `backend/services/tts_service.py`.
- Rodar novamente até 100% verde.
- Rodar toda a suíte de testes (`tests/test_services.py`, `tests/test_api.py`, etc.) para garantir zero regressões.
- Fazer commit git: `feat(tts): add voice generation controls for speed, pause, pitch and presence`.
