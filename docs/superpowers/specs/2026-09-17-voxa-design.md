# Voxa — Ferramenta Local de Clonagem de Voz, Narração e Transcrição

> **Repositório:** https://github.com/WeslleyMouraDev/Voxa.git  
> **Controle:** 100% controlável pela interface web local após inicialização.

---

## Visão Geral

O **Voxa** é uma aplicação desktop que roda 100% localmente, multiplataforma (Windows, macOS, Linux), com interface gráfica web extremamente leve servida em `localhost` (`http://localhost:7865`). Permite clonar vozes, narrar textos com voz clonada e gerar transcrições SRT precisas (com modos Normal, Dinâmico e Acelerado para sincronização com vídeos) — tudo ilimitado, rápido e sem travar a CPU ou deixar o PC lento.

---

## Stack Tecnológica

| Componente | Tecnologia | Detalhes |
|------------|------------|----------|
| **Backend** | Python 3.10+ / FastAPI | Servidor assíncrono leve com Uvicorn |
| **Frontend** | HTML5 / CSS3 / JavaScript Vanilla | SPA reativa sem build step, ultra leve e responsiva |
| **Motor TTS** | Chatterbox TTS — Single Language Pack PT-BR (`chatterbox-tts`) | Clonagem zero-shot e síntese em PT-BR |
| **Motor STT** | Faster Whisper (`faster-whisper`) | Modelo `medium` com timestamps a nível de palavra (word-level) |
| **Processamento de Áudio** | PyDub / FFmpeg / SoundFile / TorchAudio | Conversões WAV / MP3 / normalização |
| **Comunicação em Tempo Real** | Server-Sent Events (SSE) | Feedback de progresso sem polling |
| **Controle de Recursos** | `psutil` + `torch.set_num_threads` | Limite de uso de CPU (50%-75% configurável) e prioridade de processo reduzida |
| **Persistência** | Arquivos JSON locais | `data/voices.json`, `data/history.json`, `data/settings.json` |

---

## Modos de Transcrição e Geração de SRT

A ferramenta permite ao usuário escolher o formato do vídeo para o qual a legenda será sincronizada (1 imagem ou cena por bloco de legenda):

1. **Normal (4 a 6 segundos por bloco):**
   - Ideal para vídeos tradicionais, documentários e tutoriais.
   - Agrupa palavras até atingir entre 4s e 6s ou quebra em final de frase pontuada (`.`, `!`, `?`).

2. **Dinâmico (2 a 4 segundos por bloco):**
   - Ideal para Reels, TikToks, Shorts e vídeos modernos de ritmo médio.
   - Cada timestamp dura entre 2s e 4s, favorecendo cortes ágeis de imagem.

3. **Acelerado (1 a 2 segundos por bloco):**
   - Ideal para vídeos hiperdinâmicos (estilo retenção máxima / MrBeast / VSL acelerada).
   - Frases curtas de 1 a 2 segundos por bloco, sincronizadas perfeitamente com trocas de imagens ou ilustrações.

*Todos os intervalos mínimo e máximo de cada modo são 100% customizáveis na aba de Configurações da interface web.*

---

## Controle de Recursos da Máquina (Anti-Travamento)

1. **Número de Threads do PyTorch e Whisper:**
   - Detecta os núcleos lógicos e físicos via `psutil`.
   - Limita o processamento a 50% ou 75% dos núcleos (ajustável na interface).
   - Executa `torch.set_num_threads(n_threads)`.

2. **Prioridade do Processo em Background:**
   - No Windows: `p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)`.
   - No Linux/macOS: `p.nice(10)`.
   - Garante que o sistema operacional mantenha a fluidez do desktop, navegador e outras aplicações mesmo sob síntese contínua de áudio.

---

## Interface Web 100% Controlável (Dark Premium)

- **Aparência:** Tema dark refinado (#0a0a0f, #12121a, acentos roxo vibrante #7c3aed e verde #10b981).
- **Sem necessidade de terminal:** O usuário pode:
  - Adicionar vozes por upload de arquivo e testá-las na hora.
  - Definir qual voz é a padrão (marcada com estrela).
  - Digitar ou colar textos longos (com contador de caracteres).
  - Escolher se quer apenas narrar (MP3), apenas transcrever áudio existente (SRT), ou fluxo direto (MP3 + SRT sincronizados).
  - Acompanhar barra de progresso em tempo real com status descritivo via SSE.
  - Tocar o áudio gerado diretamente no player inline.
  - Baixar os arquivos `.mp3` e `.srt`.
  - Visualizar o histórico completo, selecionar itens para remoção ou limpar tudo com remoção segura dos arquivos físicos do disco.
  - Alterar configurações de CPU, modos de legenda e caminhos com salvamento automático.
