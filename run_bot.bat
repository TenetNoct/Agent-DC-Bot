@echo off
echo ===================================
echo Bot Conversacional para Discord com LM Studio
echo ===================================
echo.

echo Verificando ambiente Python...
python --version 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo Erro: Python nao encontrado! Por favor, instale o Python 3.8 ou superior.
    pause
    exit /b 1
)

echo Verificando dependencias...
pip install -r requirements.txt

echo.
echo Iniciando o bot...
echo [Pressione CTRL+C para encerrar]
echo.

python -m bot_discord.core.bot

pause