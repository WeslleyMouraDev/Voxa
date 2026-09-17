@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title Voxa — Clonagem, Narração e Transcrição PT-BR
color 0A
cls

echo.
echo  ======================================================================
echo   * VOXA - INICIALIZADOR DO SISTEMA *
echo   Clonagem, Narracao e Transcricao Inteligente PT-BR
echo  ======================================================================
echo.

cd /d "%~dp0"

:: [1/3] Verificando ambiente virtual (.venv)
echo  [1/3] Verificando ambiente virtual .venv...
if not exist ".venv\Scripts\activate.bat" goto :sem_venv
echo       Ambiente virtual localizado com sucesso!
echo.

:: [2/3] Ativando ambiente virtual...
echo  [2/3] Ativando ambiente virtual...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 goto :erro_ativar
echo       Ambiente ativado!
echo.

:: [3/3] Abrindo interface web e iniciando servidor FastAPI na porta 7865...
echo  [3/3] Iniciando o servidor Voxa e abrindo a interface web...
echo.
echo  ----------------------------------------------------------------------
echo   Servidor disponivel em: http://localhost:7865
echo   Pressione Ctrl+C no terminal para encerrar o servidor.
echo  ----------------------------------------------------------------------
echo.

start "" "http://localhost:7865"
call python -m uvicorn backend.main:app --host 127.0.0.1 --port 7865
pause
exit /b 0

:sem_venv
echo.
echo  [AVISO] Ambiente virtual nao encontrado!
echo  Por favor, execute o instalador primeiro:
echo     setup.bat
echo.
pause
exit /b 1

:erro_ativar
echo.
echo  [ERRO] Falha ao ativar o ambiente virtual .venv.
echo.
pause
exit /b 1
