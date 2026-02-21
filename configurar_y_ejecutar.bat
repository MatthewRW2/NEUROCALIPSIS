@echo off
chcp 65001 >nul
echo === Configurando proyecto pygame ===

:: Intentar usar Python 3.12
py -3.12 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python 3.12 no está instalado.
    echo.
    echo Pygame no funciona aún con Python 3.14. Necesitas Python 3.12:
    echo 1. Entra en https://www.python.org/downloads/
    echo 2. Descarga "Python 3.12.x" para Windows
    echo 3. Instálalo marcando "Add Python to PATH"
    echo 4. Vuelve a ejecutar este script: configurar_y_ejecutar.bat
    echo.
    pause
    exit /b 1
)

echo Usando Python 3.12...
if not exist "venv" (
    echo Creando entorno virtual...
    py -3.12 -m venv venv
)
call venv\Scripts\activate.bat

echo Instalando pygame...
pip install -r requirements.txt -q

echo.
echo Ejecutando juego...
python main.py

pause
