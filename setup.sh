#!/usr/bin/env bash
set -e

# Voxa — Instalador do Sistema (Linux / macOS)

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sem cor

echo -e "\n${CYAN}======================================================================${NC}"
echo -e "${CYAN} * VOXA - INSTALADOR DO SISTEMA (Linux / macOS) *${NC}"
echo -e "${CYAN}   Clonagem, Narração e Transcrição Inteligente PT-BR${NC}"
echo -e "${CYAN}======================================================================${NC}\n"

# Garante que está no diretório do script
cd "$(dirname "$0")"

# [1/4] Verificando Python 3
echo -e "${YELLOW}[1/4] Verificando Python 3.10+...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERRO] python3 não foi encontrado no sistema.${NC}"
    echo "Instale o Python 3.10+ e certifique-se de que ele esteja acessível no PATH."
    exit 1
fi
python3 -c "import sys; assert sys.version_info >= (3, 10), 'Python 3.10+ é obrigatório'"
echo -e "${GREEN}      Python 3 detectado com sucesso!${NC}\n"

# [2/4] Configurando ambiente virtual Python (.venv)
echo -e "${YELLOW}[2/4] Configurando ambiente virtual Python (.venv)...${NC}"
if [ ! -d ".venv" ]; then
    echo "      Criando novo ambiente virtual .venv..."
    python3 -m venv .venv
else
    echo "      Ambiente virtual .venv já existe."
fi

# Ativa o ambiente virtual
source .venv/bin/activate
echo -e "${GREEN}      Ambiente virtual ativado com sucesso!${NC}\n"

# [3/4] Instalando dependências (requirements.txt)
echo -e "${YELLOW}[3/4] Instalando dependências do projeto (requirements.txt)...${NC}"
echo "      Atualizando pip..."
python -m pip install --upgrade pip --quiet
echo "      Instalando pacotes necessários (aguarde)..."
python -m pip install -r requirements.txt
echo -e "${GREEN}      Dependências instaladas com sucesso!${NC}\n"

# [4/4] Verificando diretórios de dados e saída
echo -e "${YELLOW}[4/4] Verificando diretórios de trabalho...${NC}"
mkdir -p data voices output
echo -e "${GREEN}      Diretórios data, voices e output prontos!${NC}\n"

echo -e "${CYAN}======================================================================${NC}"
echo -e "${GREEN} INSTALAÇÃO CONCLUÍDA COM SUCESSO!${NC}"
echo -e "${CYAN}======================================================================${NC}\n"
echo " Para iniciar o sistema Voxa:"
echo "   ./start.sh"
echo " A interface web estará disponível em http://localhost:7865"
echo -e "\n${CYAN}======================================================================${NC}\n"
