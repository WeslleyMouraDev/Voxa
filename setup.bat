@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title Voxa - Instalador do Sistema
color 0B
cls

echo.
echo  ======================================================================
echo   * VOXA - INSTALADOR DO SISTEMA *
echo   Clonagem, Narracao e Transcricao Inteligente PT-BR
echo  ======================================================================
echo.

cd /d "%~dp0"

:: [1/4] Detectando melhor versao do Python compativel com IA
echo  [1/4] Verificando instalacao do Python compativel com pacotes de IA...

py -3.12 --version >nul 2>&1
if %errorlevel% equ 0 goto :usar_py312

py -3.11 --version >nul 2>&1
if %errorlevel% equ 0 goto :usar_py311

py -3.10 --version >nul 2>&1
if %errorlevel% equ 0 goto :usar_py310

python --version >nul 2>&1
if %errorlevel% equ 0 goto :usar_python

goto :erro_python

:usar_py312
set "PY_CMD=py -3.12"
goto :python_encontrado

:usar_py311
set "PY_CMD=py -3.11"
goto :python_encontrado

:usar_py310
set "PY_CMD=py -3.10"
goto :python_encontrado

:usar_python
set "PY_CMD=python"
goto :python_encontrado

:python_encontrado
echo       Interpretador selecionado com sucesso: !PY_CMD!
echo.

:: [2/4] Configurando ambiente virtual Python .venv
echo  [2/4] Configurando ambiente virtual Python .venv...
if exist ".venv\Scripts\activate.bat" goto :venv_ok

echo       Criando novo ambiente virtual .venv...
!PY_CMD! -m venv .venv
if %errorlevel% neq 0 goto :erro_venv
echo       Ambiente virtual criado com sucesso!
goto :ativar_venv

:venv_ok
echo       Ambiente virtual .venv ja existe e pronto para uso.

:ativar_venv
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 goto :erro_venv_ativacao
echo       Ambiente virtual ativado com sucesso!
echo.

:: [3/4] Instalando dependencias - requirements.txt
echo  [3/4] Instalando dependencias do projeto - requirements.txt...
echo       Atualizando pip no ambiente virtual...
call python -m pip install --upgrade pip --quiet
echo       Instalando pacotes necessarios - aguarde, isso pode levar alguns minutos...
call python -m pip install -r requirements.txt
if %errorlevel% neq 0 goto :erro_pip
echo       Dependencias instaladas com sucesso!
echo.

:: [4/4] Verificando diretorios de dados e saida
echo  [4/4] Verificando diretorios de trabalho...
if not exist "data" mkdir "data"
if not exist "voices" mkdir "voices"
if not exist "output" mkdir "output"
echo       Diretorios data, voices e output prontos!
echo.

echo  ======================================================================
echo   INSTALACAO CONCLUIDA COM SUCESSO!
echo  ======================================================================
echo.
echo   Para iniciar o sistema Voxa:
echo     - Execute o arquivo start.bat
echo     - A interface web abrira automaticamente em http://localhost:7865
echo.
echo  ======================================================================
echo.
pause
exit /b 0

:erro_python
echo.
echo  [ERRO] Python nao foi encontrado no sistema ou nao esta no PATH.
echo  Instale o Python 3.12 ou 3.11 e marque "Add Python to PATH".
echo.
pause
exit /b 1

:erro_venv
echo.
echo  [ERRO] Falha ao criar o ambiente virtual .venv.
echo  Verifique se o modulo venv esta instalado no seu interpretador Python.
echo.
pause
exit /b 1

:erro_venv_ativacao
echo.
echo  [ERRO] Falha ao ativar o ambiente virtual .venv.
echo.
pause
exit /b 1

:erro_pip
echo.
echo  [ERRO] Falha ao instalar as dependencias via pip.
echo  Dica: Se estiver usando Python 3.14+, use Python 3.12 ou 3.11 para evitar
echo  necessidade de compiladores C++ - Microsoft Visual C++ Build Tools.
echo.
pause
exit /b 1
