# Task 6: Interface Web Dark Premium (HTML5, CSS3, Vanilla JS Reativo)

## Objetivo
Criar uma interface gráfica web moderna, ultra leve, sem build step, 100% controlável pelo navegador, com tema Dark Premium (#0a0a0f, #12121a, acentos roxo vibrante #7c3aed e verde #10b981), tipografia elegante (Inter e JetBrains Mono), SPA fluida e integração completa com todos os endpoints da API e SSE.

## Arquivos a Criar
- `frontend/assets/logo.svg`
- `frontend/css/style.css`
- `frontend/js/api.js`
- `frontend/js/state.js`
- `frontend/js/components/toast.js`
- `frontend/js/components/modal.js`
- `frontend/js/pages/narrate.js`
- `frontend/js/pages/voices.js`
- `frontend/js/pages/history.js`
- `frontend/js/pages/settings.js`
- `frontend/js/app.js`
- `frontend/index.html`
- `tests/test_frontend.py`

## Especificações da Interface e Componentes

### 1. Paleta de Cores e Estilo Visual (`frontend/css/style.css`)
- Fundo do app: `#0a0a0f`
- Fundo de cartões/sidebar: `#12121a`
- Fundo de inputs/textareas: `#161622`
- Bordas sutis: `#222233`
- Cores de acento:
  - Roxo primário: `#7c3aed`, hover: `#9333ea`
  - Verde sucesso: `#10b981`
  - Vermelho erro/exclusão: `#ef4444`
  - Âmbar alerta: `#f59e0b`
- Tipografia: Inter (sans-serif) para texto e interface, JetBrains Mono para timestamps, códigos e durações.

### 2. Layout SPA (`frontend/index.html`)
- **Sidebar Fixa:**
  - Logo Voxa vetorial com gradiente roxo + nome Voxa e badge "PT-BR".
  - Itens de navegação:
    - 🎙 Narrar (`#narrate`)
    - 🗣 Vozes (`#voices`)
    - 📋 Histórico (`#history`)
    - ⚙ Configurações (`#settings`)
  - Status do sistema no rodapé da sidebar (indicador verde "Pronto" / roxo "Processando...").
- **Área Central:**
  - Carrega dinamicamente a página ativa sem recarregar a tela.
  - Container de Toasts flutuantes no canto superior direito.
  - Modais dinâmicos para confirmação (ex: Limpar Tudo, Nova Voz).

### 3. Módulos JavaScript
- **`frontend/js/api.js`:**
  - Wrapper para chamadas `fetch` com tratamento de erros.
  - Função `listenProgress(taskId, onMessage, onComplete, onError)` usando `EventSource` para streaming de progresso em tempo real.
- **`frontend/js/state.js`:**
  - Estado global leve: vozes carregadas, voz padrão, configurações ativas, histórico recente, tarefa em andamento.
- **`frontend/js/components/toast.js`:**
  - `showToast(message, type = "success" | "error" | "info")` com auto-dismiss suave.
- **`frontend/js/components/modal.js`:**
  - `showConfirmModal(title, message, onConfirm, confirmText, danger = false)` para confirmações seguras.
- **`frontend/js/pages/narrate.js`:**
  - Textarea com redimensionamento vertical, placeholder sugestivo e contador de caracteres em tempo real.
  - Seletor de voz com destaque para voz padrão (★) e atalho para ir cadastrar voz caso não haja nenhuma.
  - Seletor dos 3 modos de transcrição:
    - **Normal** (4-6s por bloco — ideal para 1 imagem por cena)
    - **Dinâmico** (2-4s por bloco — ideal para Reels/TikTok)
    - **Acelerado** (1-2s por bloco — ideal para retenção máxima)
  - Botões de Ação:
    - `[🎙 Apenas Narrar]` (Gera MP3)
    - `[📝 Apenas Transcrever]` (Upload de áudio existente para gerar SRT)
    - `[🎙📝 Narrar + Transcrever]` (Fluxo direto destacado gerando MP3 + SRT sincronizados)
  - Painel de Progresso Ativo:
    - Barra de progresso com porcentagem e animação de gradiente.
    - Mensagem explicativa em tempo real ("Dividindo texto...", "Sintetizando voz...", "Gerando timestamps de precisão...").
  - Painel de Resultado:
    - Player de áudio HTML5 com controles elegantes.
    - Botões de download do MP3 e download do arquivo SRT.
- **`frontend/js/pages/voices.js`:**
  - Lista de vozes cadastradas em grid de cards.
  - Em cada card: nome, player de amostra da voz, botão de estrela para definir como padrão instantaneamente, e botão de lixeira para excluir.
  - Botão `[+ Adicionar Nova Voz]` que abre modal:
    - Campo de nome/apelido.
    - Input para upload de áudio de referência (WAV, MP3 de 5 a 30s).
    - Checkbox "Definir como voz padrão".
    - Envio multipart e atualização imediata da lista.
- **`frontend/js/pages/history.js`:**
  - Barra de topo com resumo de itens e botão `[🗑 Limpar Histórico Completo]` com modal de confirmação.
  - Tabela ou lista de cards com:
    - Trecho do texto narrado.
    - Data e hora formatada.
    - Voz utilizada.
    - Modo de legenda usado.
    - Player de áudio embutido.
    - Botão de baixar MP3 e baixar SRT (se disponível).
    - Botão de excluir item individualmente.
- **`frontend/js/pages/settings.js`:**
  - Slider interativo de limitação de CPU (25% a 100%) exibindo a quantidade estimada de núcleos.
  - Configuração de durações mínimas e máximas para os 3 modos (Normal, Dinâmico, Acelerado).
  - Porta do servidor e alternador de abrir navegador automaticamente.
  - Botão "Salvar Configurações" com feedback toast instantâneo.

## Requisitos de Testes (`tests/test_frontend.py`)
- Testar que a rota raiz `/` serve o `index.html` com status 200 e tipo `text/html`.
- Testar que os arquivos estáticos de CSS, JS e SVG são acessíveis com status 200.
- Testar que o HTML possui referências aos arquivos CSS e JS corretos.

## Comandos
- Testes: `python -m pytest tests/test_frontend.py -v`
- Commits: `git add frontend/ tests/test_frontend.py && git commit -m "feat: create dark premium web interface with full spa controls, sse progress, and audio player"`
