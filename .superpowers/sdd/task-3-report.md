# Relatório da Task 3: Controles de Geração no Motor TTS (Ritmo, Pausa, Tom, Presença)

## Visão Geral
- **Data:** 18/09/2026
- **Status:** Concluído com sucesso (DONE)
- **Commit:** `7b327ca` (`feat(tts): add voice generation controls for speed, pause, pitch and presence`)

## Alterações Realizadas

### 1. `backend/services/tts_service.py`
- **Assinatura de `generate_speech`**:
  - Adicionados os parâmetros: `speed: float = 1.0`, `max_pause: float = 0.3`, `pitch: float = 0.0`, `presence: float = 0.5`.
- **Presença vocal (`presence`)**:
  - Inspeciona se `"exaggeration"` está na assinatura do método `generate` ou se aceita `**kwargs`.
  - Passa `kwargs["exaggeration"] = float(presence)` para o modelo Chatterbox.
- **Pausa máxima entre sentenças (`max_pause`)**:
  - Na concatenação de múltiplos chunks (`len(audio_chunks) > 1` e `max_pause > 0`):
    - Calcula `pause_samples = int(sample_rate * max_pause)`.
    - Intercala `silence_array = np.zeros(pause_samples, dtype=np.float32)` entre cada chunk adjacente.
    - Preserva o áudio original sem pausas para textos com chunk único ou quando `max_pause <= 0`.
- **Ritmo (`speed`) e Tom (`pitch`)**:
  - Novo método estático auxiliar `_build_atempo_chain(tempo: float) -> str`:
    - Suporta qualquer multiplicador positivo, particionando fatores fora do intervalo `[0.5, 2.0]` em filtros encadeados (`atempo=2.0,...` ou `atempo=0.5,...`).
  - Atualização do método `_export_to_mp3(audio_arr, sample_rate, output_path, speed=1.0, pitch=0.0)`:
    - Se `pitch != 0.0`:
      - Calcula escala de semitons `pitch_scale = 2.0 ** (pitch / 12.0)`.
      - Define `new_rate = int(sample_rate * pitch_scale)` e tempo de compensação `total_tempo = (1.0 / pitch_scale) * speed`.
      - Monta filtro: `f"asetrate={new_rate},aresample={sample_rate},{atempo_chain}"`.
    - Se `pitch == 0.0` e `speed != 1.0`:
      - Monta filtro: `_build_atempo_chain(speed)`.
    - Se houver filtro de áudio, insere `-af <audio_filter>` nos argumentos do FFmpeg.
    - Se não houver filtros (`speed == 1.0` e `pitch == 0.0`), executa comando FFmpeg sem `-af`, mantendo comportamento idêntico ao legado e fallback íntegro.

### 2. `tests/test_voice_controls.py` (Novo)
- 5 testes automatizados cobrindo os requisitos:
  1. `test_presence_passed_as_exaggeration`: valida repasse de `presence` customizado e default como `exaggeration`.
  2. `test_max_pause_silence_between_chunks`: valida tamanho de amostras e fatias de silêncio (zeros) entre múltiplos chunks.
  3. `test_max_pause_zero_and_single_chunk`: garante ausência de silêncio extra para chunk único ou `max_pause=0.0`.
  4. `test_speed_and_pitch_ffmpeg_filters`: valida construção de argumentos `-af` (ausência de flag no default, encadeamento para `speed=0.4`, e fórmulas de `asetrate`/`aresample`/`atempo` para variações de tom em semitons).
  5. `test_generate_speech_backward_compatibility`: assegura compatibilidade retroativa para chamadas legadas com defaults.

## Ciclo TDD e Verificação

1. **RED (Fase de Falha):**
   - Execução: `.venv\Scripts\python.exe -m pytest tests/test_voice_controls.py -v`
   - Resultado: 5 falhas esperadas (`TypeError` por ausência de parâmetros e `AssertionError`).
2. **GREEN (Fase de Implementação e Sucesso):**
   - Execução: `.venv\Scripts\python.exe -m pytest tests/test_voice_controls.py -v`
   - Resultado: 5 testes passaram em 0.50s (100% verde).
3. **Regressão Completa:**
   - Execução: `.venv\Scripts\python.exe -m pytest tests/ -v`
   - Resultado: 122 testes passaram em 23.72s (100% verde, zero regressões nos 117 testes prévios).
4. **Knowledge Graph:**
   - Atualizado via `graphify update .` (688 nós, 886 arestas, 70 comunidades).

## Preocupações / Observações
- A cadeia de filtros `atempo` foi construída para manter precisão de 4 casas decimais e suportar valores extremos sem extrapolar os limites aceitos pelo FFmpeg (`0.5` a `2.0`).
- O fallback para conversão direta/WAV caso o FFmpeg não esteja disponível no ambiente do usuário foi preservado sem impacto.
