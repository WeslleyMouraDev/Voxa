/**
 * Voxa API Documentation Page
 * Documentação interativa da API REST, endpoints, snippets cURL e atalho Swagger.
 */

import { showToast } from '../components/toast.js';

export function renderApiDocsPage(container) {
  const baseUrl = window.location.origin || 'http://localhost:8000';

  const endpoints = [
    {
      group: '🎙️ Narração & Transcrição',
      description: 'Gere áudios sintetizados com clonagem de voz e legendas SRT sincronizadas.',
      items: [
        {
          method: 'POST',
          path: '/api/narrate',
          title: 'Iniciar Narração',
          desc: 'Sintetiza áudio a partir de um texto em português, com suporte opcional a clonagem de voz e controles moduláveis (ritmo, pausa, tom, presença). Retorna o task_id assíncrono.',
          curl: `curl -X POST "${baseUrl}/api/narrate" \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "Bem-vindo ao Voxa, seu estúdio local de narração por IA!",
    "voice_id": null,
    "speed": 1.0,
    "max_pause": 0.3,
    "pitch": 0.0,
    "presence": 0.5
  }'`
        },
        {
          method: 'POST',
          path: '/api/narrate-and-transcribe',
          title: 'Narrar e Transcrever (Pipeline Completo)',
          desc: 'Executa a síntese de voz e a transcrição Whisper em pipeline único, gerando tanto o áudio (.mp3) quanto as legendas dinâmicas (.srt) milimetricamente alinhadas.',
          curl: `curl -X POST "${baseUrl}/api/narrate-and-transcribe" \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "Este roteiro será narrado e transcrito automaticamente em modo dinâmico.",
    "mode": "dynamic",
    "voice_id": null,
    "speed": 1.0,
    "max_pause": 0.3,
    "pitch": 0.0,
    "presence": 0.5
  }'`
        },
        {
          method: 'POST',
          path: '/api/transcribe',
          title: 'Apenas Transcrever Áudio',
          desc: 'Gera arquivo de legendas SRT a partir do upload de um arquivo de áudio existente (MP3, WAV, M4A, etc.) com segmentação baseada no modo escolhido (normal, dynamic, accelerated).',
          curl: `curl -X POST "${baseUrl}/api/transcribe" \\
  -F "file=@/caminho/para/audio.mp3" \\
  -F "mode=dynamic"`
        },
        {
          method: 'GET',
          path: '/api/progress/{task_id}',
          title: 'Monitorar Progresso (SSE)',
          desc: 'Stream Server-Sent Events (SSE) que emite eventos em tempo real com a porcentagem e etapa atual da tarefa até a sua conclusão.',
          curl: `curl -N -H "Accept: text/event-stream" \\
  "${baseUrl}/api/progress/f81d4fae-7dec-11d0-a765-00a0c91e6bf6"`
        }
      ]
    },
    {
      group: '🗣️ Gerenciamento de Vozes',
      description: 'Cadastre, consulte e gerencie amostras de vozes clonadas.',
      items: [
        {
          method: 'GET',
          path: '/api/voices',
          title: 'Listar Vozes',
          desc: 'Retorna a lista de todas as vozes cadastradas com seus identificadores, nomes e indicador de voz padrão.',
          curl: `curl -X GET "${baseUrl}/api/voices"`
        },
        {
          method: 'POST',
          path: '/api/voices',
          title: 'Cadastrar Nova Voz',
          desc: 'Faz o upload de uma amostra de áudio limpa (de 5 a 15 segundos) para cadastrar uma nova voz clonada no sintetizador.',
          curl: `curl -X POST "${baseUrl}/api/voices" \\
  -F "name=Apresentador Principal" \\
  -F "sample_file=@/caminho/para/amostra.wav"`
        },
        {
          method: 'PUT',
          path: '/api/voices/{id}/default',
          title: 'Definir Voz Padrão',
          desc: 'Marca a voz especificada como a voz padrão utilizada automaticamente nas requisições sem voice_id definido.',
          curl: `curl -X PUT "${baseUrl}/api/voices/voice_123/default"`
        },
        {
          method: 'DELETE',
          path: '/api/voices/{id}',
          title: 'Excluir Voz',
          desc: 'Exclui o registro da voz e remove sua amostra de áudio do armazenamento local.',
          curl: `curl -X DELETE "${baseUrl}/api/voices/voice_123"`
        }
      ]
    },
    {
      group: '📋 Histórico de Produções',
      description: 'Acesse e gerencie as gravações e legendas geradas anteriormente.',
      items: [
        {
          method: 'GET',
          path: '/api/history',
          title: 'Listar Histórico',
          desc: 'Retorna a lista cronológica decrescente de todas as tarefas finalizadas, com links diretos para download de áudio e legendas.',
          curl: `curl -X GET "${baseUrl}/api/history"`
        },
        {
          method: 'DELETE',
          path: '/api/history/{id}',
          title: 'Excluir Item do Histórico',
          desc: 'Remove um item específico do histórico e deleta seus arquivos associados em disco (.mp3, .srt).',
          curl: `curl -X DELETE "${baseUrl}/api/history/hist_456"`
        },
        {
          method: 'DELETE',
          path: '/api/history',
          title: 'Limpar Todo o Histórico',
          desc: 'Remove todas as entradas de histórico e arquivos gerados (ação irreversível).',
          curl: `curl -X DELETE "${baseUrl}/api/history"`
        }
      ]
    },
    {
      group: '🖥️ Logs, Métricas & Telemetria',
      description: 'Acompanhe a saúde do sistema, consumo de CPU/RAM e logs em tempo real.',
      items: [
        {
          method: 'GET',
          path: '/api/logs',
          title: 'Consultar Logs',
          desc: 'Consulta as entradas do buffer circular de logs em memória, permitindo filtrar por nível (DEBUG, INFO, WARNING, ERROR), busca textual e limite.',
          curl: `curl -X GET "${baseUrl}/api/logs?level=ERROR&limit=50"`
        },
        {
          method: 'DELETE',
          path: '/api/logs',
          title: 'Limpar Logs',
          desc: 'Esvazia o buffer circular de logs em memória.',
          curl: `curl -X DELETE "${baseUrl}/api/logs"`
        },
        {
          method: 'WS',
          path: '/api/ws/logs',
          title: 'WebSocket de Logs & Telemetria',
          desc: 'Canal WebSocket bidirecional para streaming contínuo de logs recém-gerados e métricas periódicas de hardware (CPU, RAM).',
          curl: `# Exemplo de conexão com wscat
npx wscat -c "ws://localhost:8000/api/ws/logs"`
        },
        {
          method: 'GET',
          path: '/api/system/metrics',
          title: 'Métricas de Sistema',
          desc: 'Retorna informações instantâneas sobre carga de CPU, uso de memória RAM e integridade geral da máquina.',
          curl: `curl -X GET "${baseUrl}/api/system/metrics"`
        }
      ]
    },
    {
      group: '⚙️ Configurações do Sistema',
      description: 'Consulte e ajuste os parâmetros operacionais dos motores de IA e limites de hardware.',
      items: [
        {
          method: 'GET',
          path: '/api/settings',
          title: 'Obter Configurações',
          desc: 'Retorna o conjunto atual de parâmetros de TTS, STT, limitação de threads de CPU e diretórios de saída.',
          curl: `curl -X GET "${baseUrl}/api/settings"`
        },
        {
          method: 'PUT',
          path: '/api/settings',
          title: 'Atualizar Configurações',
          desc: 'Salva novas configurações de hardware e modelos para aplicação imediata nos pipelines.',
          curl: `curl -X PUT "${baseUrl}/api/settings" \\
  -H "Content-Type: application/json" \\
  -d '{
    "whisper_model": "base",
    "device": "cpu",
    "cpu_limit_percent": 80
  }'`
        }
      ]
    }
  ];

  container.innerHTML = `
    <div class="page-container api-docs-container">
      <div class="page-header api-docs-header">
        <div>
          <h1 class="page-title"><span>📚</span> Documentação da API REST & Integração Externa</h1>
          <p class="page-subtitle">Guia completo para controlar o Voxa de forma 100% programática via requisições HTTP e WebSockets.</p>
        </div>
        <div class="api-docs-actions">
          <a href="/docs" target="_blank" rel="noopener noreferrer" class="btn btn-primary" id="btn-open-swagger" title="Abrir interface interativa OpenAPI / Swagger">
            <span>🚀</span> Abrir Swagger UI (/docs)
          </a>
        </div>
      </div>

      <!-- Card Informativo de Destaque -->
      <div class="card api-overview-card">
        <div class="api-overview-content">
          <div class="api-overview-item">
            <span class="api-overview-label">URL Base Local:</span>
            <code class="api-code-inline" id="api-base-url">${baseUrl}</code>
          </div>
          <div class="api-overview-item">
            <span class="api-overview-label">Formato Padrão:</span>
            <code class="api-code-inline">application/json</code>
          </div>
          <div class="api-overview-item">
            <span class="api-overview-label">Documentação Interativa:</span>
            <a href="/docs" target="_blank" rel="noopener noreferrer" class="api-docs-link">Swagger UI (/docs)</a>
            <span class="separator">•</span>
            <a href="/redoc" target="_blank" rel="noopener noreferrer" class="api-docs-link">ReDoc (/redoc)</a>
          </div>
        </div>
      </div>

      <!-- Grupos de Endpoints -->
      <div class="api-groups-container">
        ${endpoints
          .map(
            (group, gIdx) => `
          <div class="api-group-section">
            <div class="api-group-header">
              <h2 class="api-group-title">${group.group}</h2>
              <p class="api-group-desc">${group.description}</p>
            </div>

            <div class="api-endpoints-list">
              ${group.items
                .map(
                  (item, iIdx) => `
                <div class="api-endpoint-card" id="endpoint-${gIdx}-${iIdx}">
                  <div class="api-endpoint-header">
                    <div class="api-endpoint-badge-and-path">
                      <span class="method-badge method-${item.method.toLowerCase()}">${item.method}</span>
                      <code class="api-path">${item.path}</code>
                    </div>
                    <span class="api-endpoint-name">${item.title}</span>
                  </div>

                  <p class="api-endpoint-desc">${item.desc}</p>

                  <div class="api-curl-block">
                    <div class="api-curl-header">
                      <span class="api-curl-title">Exemplo cURL</span>
                      <button class="btn-copy-curl" data-curl="${encodeURIComponent(item.curl)}" title="Copiar comando cURL para a área de transferência">
                        <span class="copy-icon">📋</span> Copiar cURL
                      </button>
                    </div>
                    <pre class="api-curl-code"><code>${escapeHtml(item.curl)}</code></pre>
                  </div>
                </div>
              `
                )
                .join('')}
            </div>
          </div>
        `
          )
          .join('')}
      </div>
    </div>
  `;

  setupApiDocsEvents(container);
}

function setupApiDocsEvents(container) {
  const copyButtons = container.querySelectorAll('.btn-copy-curl');

  copyButtons.forEach((btn) => {
    btn.addEventListener('click', async () => {
      const curlCommand = decodeURIComponent(btn.getAttribute('data-curl') || '');
      if (!curlCommand) return;

      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(curlCommand);
        } else {
          // Fallback para navegadores sem permissão de clipboard direto
          const textarea = document.createElement('textarea');
          textarea.value = curlCommand;
          textarea.style.position = 'fixed';
          textarea.style.opacity = '0';
          document.body.appendChild(textarea);
          textarea.select();
          document.execCommand('copy');
          document.body.removeChild(textarea);
        }

        const originalHtml = btn.innerHTML;
        btn.innerHTML = '<span class="copy-icon">✓</span> Copiado!';
        btn.classList.add('copied');
        showToast('Comando cURL copiado para a área de transferência!', 'success');

        setTimeout(() => {
          btn.innerHTML = originalHtml;
          btn.classList.remove('copied');
        }, 2000);
      } catch (err) {
        showToast('Falha ao copiar cURL. Copie manualmente.', 'error');
        console.error('Erro ao copiar comando:', err);
      }
    });
  });
}

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
