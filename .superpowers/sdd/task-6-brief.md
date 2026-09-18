# Task 6 Brief: Interface Web — Controles de Geração (Accordion) e Página #api-docs

## Objetivo
Implementar na interface web do Voxa:
1. O componente retrátil (Accordion) "🎛️ Ajustes de Voz & Estilo" na tela de narração, com sliders interativos para Ritmo, Pausa máxima, Tom e Presença, valores em tempo real, botão de reset e envio dos parâmetros nas chamadas de síntese.
2. Atualizar o cliente `frontend/js/api.js` para enviar os parâmetros de controle de voz.
3. Criar a nova página `#api-docs` (`frontend/js/pages/api-docs.js`) com catálogo completo dos endpoints REST em PT-BR, snippets `curl` com botão de copiar e atalho para o Swagger interativo (`/docs`).
4. Integrar a rota `#api-docs` no roteador da SPA (`frontend/js/app.js`) e adicionar atalho na navegação.

## Arquivos a Criar / Modificar
- Modificar: `frontend/js/pages/narrate.js`
- Modificar: `frontend/js/api.js`
- Criar: `frontend/js/pages/api-docs.js`
- Modificar: `frontend/js/app.js`
- Modificar: `frontend/css/style.css`
- Modificar: `tests/test_frontend.py`
- Relatório: `d:\Projetos\Voxa\.superpowers\sdd\task-6-report.md`

## Requisitos Técnicos

### 1. `frontend/js/pages/narrate.js`
- Adicionar o Accordion entre o seletor de voz e os modos de legenda:
  - Header: `🎛️ Ajustes de Voz & Estilo (Ritmo, Pausa, Tom, Presença)`
  - Botão de reset rápido: `↺ Resetar`
  - Indicador de estado (aberto/fechado com persistência no `localStorage`)
  - 4 sliders:
    1. **Ritmo (Velocidade)**: id `voice-speed`, range `0.5` a `2.0`, step `0.05`, default `1.0`, mostrador `1.0x`.
    2. **Pausa Máxima**: id `voice-max-pause`, range `0.0` a `2.0`, step `0.05`, default `0.3`, mostrador `300ms` / `0.3s`.
    3. **Tom (Pitch)**: id `voice-pitch`, range `-12` a `12`, step `1`, default `0`, mostrador `0 st` (Normal).
    4. **Presença Vocal**: id `voice-presence`, range `0.0` a `1.0`, step `0.05`, default `0.5`, mostrador `50%`.
- Salvar e restaurar valores do `localStorage` (`voxa_voice_speed`, `voxa_voice_max_pause`, etc.).
- Nos botões `btn-narrate-only` e `btn-narrate-transcribe`:
  - Ler valores dos 4 sliders e repassar para `api.startNarration` e `api.startNarrationAndTranscription`.

### 2. `frontend/js/api.js`
- Atualizar `startNarration(text, voiceId = null, controls = {})`:
  ```javascript
  const payload = { text, ...controls };
  if (voiceId) payload.voice_id = voiceId;
  ```
- Atualizar `startNarrationAndTranscription(text, voiceId = null, mode = 'normal', controls = {})`:
  ```javascript
  const payload = { text, mode, ...controls };
  if (voiceId) payload.voice_id = voiceId;
  ```

### 3. `frontend/js/pages/api-docs.js`
- Exportar `renderApiDocsPage(container)`.
- Estrutura da página:
  - Título: `📚 Documentação da API REST & Integração Externa`
  - Descrição: Documentação completa para controle programático do Voxa 100% via API.
  - Botão de destaque: `🚀 Abrir Swagger UI (/docs)` (abre em nova aba ou exibe iframe integrado).
  - Listagem dos endpoints agrupados:
    - **Narração & Transcrição**: `POST /api/narrate`, `POST /api/narrate-and-transcribe`, `POST /api/transcribe`, `GET /api/progress/{task_id}`.
    - **Vozes**: `GET /api/voices`, `POST /api/voices`, `PUT /api/voices/{id}/default`, `DELETE /api/voices/{id}`.
    - **Histórico**: `GET /api/history`, `DELETE /api/history/{id}`, `DELETE /api/history`.
    - **Logs & Sistema**: `GET /api/logs`, `DELETE /api/logs`, `WS /api/ws/logs`, `GET /api/system/metrics`.
    - **Configurações**: `GET /api/settings`, `PUT /api/settings`.
  - Cada endpoint inclui:
    - Badge do método (GET, POST, PUT, DELETE, WS) com cor diferenciada.
    - Endpoint path e descrição em PT-BR.
    - Bloco de comando `curl` com exemplo pronto para executar.
    - Botão interativo `📋 Copiar cURL` com feedback visual de confirmação.

### 4. `frontend/js/app.js`
- Registrar `api-docs: renderApiDocsPage` nas rotas do SPA.
- Adicionar link da API no menu lateral da sidebar (`#api-docs` com ícone 📚 ou 🔌).

### 5. `frontend/css/style.css`
- Estilização do accordion de ajustes de voz e dos sliders customizados.
- Estilização dos blocos de documentação da API, badges de métodos HTTP e botões de copiar cURL.

### 6. Ciclo TDD
- Adicionar testes em `tests/test_frontend.py` validando os novos componentes e rotas.
- Rodar `.venv\Scripts\python.exe -m pytest tests/test_frontend.py -v`.
- Rodar a suíte global de testes (`pytest tests/ -v`) para garantir zero regressões.
- Fazer commit git: `feat(ui): add voice adjustments accordion and api documentation page`.
