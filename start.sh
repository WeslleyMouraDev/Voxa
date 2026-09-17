#!/usr/bin/env bash
set -e

# Voxa — Inicializador do Sistema (Linux / macOS)

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "\n${CYAN}======================================================================${NC}"
echo -e "${CYAN} * VOXA - INICIALIZADOR DO SISTEMA (Linux / macOS) *${NC}"
echo -e "${CYAN}   Clonagem, Narração e Transcrição Inteligente PT-BR${NC}"
echo -e "${CYAN}======================================================================${NC}\n"

cd "$(dirname "$0")"

# [1/3] Verificando ambiente virtual (.venv)
echo -e "${YELLOW}[1/3] Verificando ambiente virtual (.venv)...${NC}"
if [ ! -f ".venv/bin/activate" ]; then
    echo -e "${RED}[AVISO] Ambiente virtual não encontrado!${NC}"
    echo "Por favor, execute o instalador primeiro:"
    echo "   ./setup.sh"
    exit 1
fi
echo -e "${GREEN}      Ambiente virtual localizado com sucesso!${NC}\n"

# [2/3] Ativando ambiente virtual...
echo -e "${YELLOW}[2/3] Ativando ambiente virtual...${NC}"
source .venv/bin/activate
echo -e "${GREEN}      Ambiente ativado!${NC}\n"

# [3/3] Abrindo interface web e iniciando servidor FastAPI na porta 7865...
echo -e "${YELLOW}[3/3] Iniciando o servidor Voxa na porta 7865...${NC}\n"
echo -e "${CYAN}----------------------------------------------------------------------${NC}"
echo -e "${GREEN} Servidor disponível em: http://localhost:7865${NC}"
echo -e " Pressione Ctrl+C para encerrar o servidor."
echo -e "${CYAN}----------------------------------------------------------------------${NC}\n"

# Tenta abrir o navegador em segundo plano se utilitário existir
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:7865" >/dev/null 2>&1 &
elif command -v open &> /dev/null; then
    open "http://localhost:7865" >/dev/null 2>&1 &
fi

exec python -m uvicorn backend.main:app --host 127.0.0.1 --port 7865
