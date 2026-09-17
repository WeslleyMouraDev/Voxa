# Task 4: Motores de IA TTS (Chatterbox PT-BR) e STT (Faster Whisper) com Chunking

## Objetivo
Implementar os wrappers de serviços de inteligência artificial:
1. `backend/services/tts_service.py`: Motor de síntese de voz e clonagem usando Chatterbox TTS Single Language Pack PT-BR, com sanitização de texto, divisão em sentenças/chunks para evitar truncamento em textos longos, concatenação de áudios e exportação para MP3.
2. `backend/services/stt_service.py`: Motor de transcrição de áudio usando Faster Whisper, com extração de word-level timestamps e integração com o `SRTBuilder`.

## Arquivos a Criar
- `backend/services/tts_service.py`
- `backend/services/stt_service.py`
- `tests/test_services.py`

## Especificações Técnicas e Interfaces

### 1. `backend/services/tts_service.py`
- Classe `TTSService`:
  - `split_text_into_chunks(text: str, max_chars: int = 250) -> list[str]`:
    - Normaliza espaços em branco e quebras de linha.
    - Divide o texto em sentenças baseado em pontuação (`.`, `!`, `?`, `\n`).
    - Se uma sentença individual for maior que `max_chars`, divide por vírgulas ou espaços.
    - Junta frases menores até atingir aproximadamente `max_chars`, sem quebrar palavras ao meio.
    - Retorna lista de chunks não vazios.
  - `__init__(cpu_limiter: Optional[CPULimiter] = None)`:
    - Armazena referência ao `cpu_limiter`.
    - Lazy loading ou carregamento sob demanda do modelo `ChatterboxTTS`.
    - Suporte a fallback inteligente para mock/ambiente de teste ou quando a biblioteca não puder carregar pesos pesados no teste unitário.
  - `generate_speech(text: str, voice_sample_path: str | Path, output_mp3_path: str | Path, progress_callback: Optional[Callable[[float, str], None]] = None) -> Path`:
    - Aplica limites de CPU antes da inferência via `cpu_limiter.apply_limits()`.
    - Divide `text` em chunks via `split_text_into_chunks`.
    - Notifica progresso via `progress_callback(percent, msg)` para cada chunk processado.
    - Sintetiza áudio de cada chunk com `audio_prompt_path=str(voice_sample_path)`.
    - Concatena os áudios gerados em um arquivo único.
    - Converte / salva em formato MP3 no caminho especificado `output_mp3_path` (criando diretórios pais se necessário).
    - Retorna `Path(output_mp3_path)`.

### 2. `backend/services/stt_service.py`
- Classe `STTService`:
  - `__init__(cpu_limiter: Optional[CPULimiter] = None, model_size: str = "medium")`:
    - Armazena referência ao `cpu_limiter` e `model_size`.
    - Lazy loading ou carregamento sob demanda do `WhisperModel` do `faster_whisper`.
  - `transcribe_audio(audio_path: str | Path, mode: TranscriptionMode = TranscriptionMode.NORMAL, mode_config: Optional[dict] = None, progress_callback: Optional[Callable[[float, str], None]] = None) -> tuple[str, list[WordTimestamp], float]`:
    - Aplica limites de CPU via `cpu_limiter.apply_limits()`.
    - Notifica progresso inicial: `progress_callback(10.0, "Iniciando transcrição com Whisper...")`.
    - Executa a transcrição com `language="pt"`, `word_timestamps=True`, `vad_filter=True`.
    - Extrai cada palavra com `WordTimestamp(word=w.word.strip(), start=w.start, end=w.end, probability=w.probability)`.
    - Calcula a duração total do áudio em segundos.
    - Usa `SRTBuilder.build_srt(words, mode=mode, min_seconds=..., max_seconds=...)` para gerar o conteúdo SRT.
    - Notifica progresso final: `progress_callback(100.0, "Transcrição concluída.")`.
    - Retorna tupla: `(srt_content, list_of_words, total_duration_seconds)`.

## Requisitos de Testes (`tests/test_services.py`)
- Testes unitários para `split_text_into_chunks`:
  - Testar texto curto (< max_chars) gerando 1 chunk.
  - Testar texto longo com múltiplas frases gerando múltiplos chunks respeitando pontuações.
  - Testar texto sem pontuação dividindo por limites de caracteres sem quebrar palavras no meio.
- Testes com Mock para `TTSService.generate_speech`:
  - Mockar o modelo Chatterbox gerando áudio simulado.
  - Verificar se o `progress_callback` é chamado para cada chunk com valores crescentes.
  - Verificar se o arquivo MP3 de saída é criado no disco.
- Testes com Mock para `STTService.transcribe_audio`:
  - Mockar o `WhisperModel.transcribe` retornando segmentos e palavras mockadas.
  - Verificar geração do conteúdo SRT nos modos Normal, Dinâmico e Acelerado.
  - Verificar chamada correta do `progress_callback`.

## Comandos
- Testes: `python -m pytest tests/test_services.py -v`
- Commits: `git add backend/services/ tests/test_services.py && git commit -m "feat: implement chatterbox tts and faster whisper stt services with chunking"`
