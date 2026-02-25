@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === Compilando NEUROCALIPSIS a .exe portable ===
echo.

:: Asegurar que exista el venv y que tenga pygame (mismo que para jugar)
if not exist "venv\Scripts\python.exe" (
    echo No hay entorno virtual. Creando con Python 3.12...
    py -3.12 -m venv venv 2>nul
    if errorlevel 1 (
        echo [ERROR] Instala Python 3.12 o ejecuta antes: configurar_y_ejecutar.bat
        pause
        exit /b 1
    )
)

:: Usar SIEMPRE el Python del venv (ahí está instalado pygame)
set PYEXE=venv\Scripts\python.exe
set PIPEXE=venv\Scripts\pip.exe

echo Comprobando pygame en el venv...
"%PYEXE%" -c "import pygame" 2>nul
if errorlevel 1 (
    echo Instalando dependencias en el venv (pygame, pyinstaller)...
    "%PIPEXE%" install -r requirements.txt -q
    "%PIPEXE%" install pyinstaller -q
)

echo Instalando PyInstaller en el venv si falta...
"%PIPEXE%" install pyinstaller -q

echo.
echo Compilando con el Python del venv (el que tiene pygame)...
echo Esto puede tardar 1-2 minutos.
echo.

"%PYEXE%" -m PyInstaller --clean --noconfirm neurocalipsis.spec

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo   Compilación correcta.
    echo   Ejecutable: dist\Neurocalipsis.exe
    echo ============================================
    echo.
    echo Puedes copiar dist\Neurocalipsis.exe a cualquier PC con Windows;
    echo no hace falta tener Python instalado.
    echo.
) else (
    echo.
    echo [ERROR] La compilación falló. Revisa los mensajes anteriores.
    echo.
)

pause
