# Task 3: Algoritmo de Geração de Legenda SRT Inteligente (3 Modos)

## Objetivo
Implementar o módulo `backend/services/srt_builder.py` para converter uma lista de palavras com timestamps (`WordTimestamp`) em um arquivo de legendas `.srt` perfeitamente sincronizado com um dos 3 formatos de vídeo:
- **Normal:** 4 a 6 segundos por bloco (para 1 imagem/cena a cada 4-6s)
- **Dinâmico:** 2 a 4 segundos por bloco (para cortes médios/Reels/TikToks)
- **Acelerado:** 1 a 2 segundos por bloco (para cortes rápidos/VSL acelerada)

## Arquivos a Criar
- `backend/services/srt_builder.py`
- `tests/test_srt_builder.py`

## Especificações Técnicas e Interfaces

### 1. `backend/services/srt_builder.py`
- Dataclass / Model `WordTimestamp`:
  - `word: str`
  - `start: float` (em segundos)
  - `end: float` (em segundos)
  - `probability: float = 1.0`
- Dataclass / Model `SRTSegment`:
  - `index: int`
  - `start: float`
  - `end: float`
  - `text: str`
- Classe `SRTBuilder`:
  - `format_timestamp(seconds: float) -> str`:
    - Converte float em string de formato SRT: `HH:MM:SS,mmm`
    - Exemplo: `0.0` -> `00:00:00,000`, `65.432` -> `00:01:05,432`.
  - `build_segments(words: list[WordTimestamp], mode: TranscriptionMode = TranscriptionMode.NORMAL, min_seconds: Optional[float] = None, max_seconds: Optional[float] = None) -> list[SRTSegment]`:
    - Se `min_seconds` ou `max_seconds` não forem fornecidos, obtém os padrões do enum:
      - `NORMAL`: min=4.0, max=6.0
      - `DYNAMIC`: min=2.0, max=4.0
      - `ACCELERATED`: min=1.0, max=2.0
    - Algoritmo de agrupamento:
      - Agrupa palavras consecutivas em um segmento corrente.
      - A duração do segmento é `current_end - current_start`.
      - Quebra de segmento ocorre quando:
        1. O segmento atingiu a duração mínima (`min_seconds`) E a palavra atual termina com pontuação forte (`.`, `!`, `?`, `;`, `\n`)
        2. OU a duração atinge ou excede a duração máxima (`max_seconds`)
        3. OU há um silêncio substancial entre a palavra anterior e a atual (ex: `word.start - prev_word.end >= 1.0` segundos) e o segmento já tem pelo menos `min_seconds * 0.7` segundos.
      - Ao quebrar, inicia um novo segmento para a próxima palavra.
      - No final, adiciona o último segmento acumulado se houver palavras.
      - Garante que cada segmento tenha índice sequencial 1, 2, 3...
  - `build_srt(words: list[WordTimestamp], mode: TranscriptionMode = TranscriptionMode.NORMAL, min_seconds: Optional[float] = None, max_seconds: Optional[float] = None) -> str`:
    - Constrói a string final no formato padrão SRT:
      ```
      1
      00:00:00,000 --> 00:00:04,500
      Olá, bem-vindos ao nosso canal.

      2
      00:00:04,500 --> 00:00:08,200
      Hoje vamos falar sobre inteligência artificial.
      ```
      (com quebras de linha duplas entre segmentos).
  - `save_srt_file(srt_content: str, destination_path: Path) -> Path`:
    - Salva o arquivo no disco garantindo encoding `utf-8`.

## Requisitos de Testes (`tests/test_srt_builder.py`)
- Testar formatação de timestamps (`format_timestamp`).
- Testar geração de SRT vazio (sem palavras -> string vazia).
- Testar modo Normal (garantindo que segmentos respeitem as durações de ~4s a 6s).
- Testar modo Dinâmico (segmentos de ~2s a 4s).
- Testar modo Acelerado (segmentos de ~1s a 2s).
- Testar respeito a pontuações (`.` quebrando segmentos quando após `min_seconds`).
- Testar quebras por pausas de silêncio.
- Testar `save_srt_file` escrevendo arquivo legível no disco.

## Comandos
- Testes: `python -m pytest tests/test_srt_builder.py -v`
- Commits: `git add backend/services/srt_builder.py tests/test_srt_builder.py && git commit -m "feat: implement intelligent srt generator for normal, dynamic, and accelerated modes"`
