@echo off
title PDF Image Converter - MVC Edition
echo.
echo 🎨 ================================================
echo    PDF Image Converter - MVC Edition
echo ================================================
echo.
echo 🏗️ Arquitectura MVC • Efectos de Color • Union PDF
echo.

cd /d "%~dp0"

:: Verificar si Python está disponible
C:/Python313/python.exe --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no encontrado
    echo Asegurate de que Python este instalado correctamente
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

:: Verificar si existe el ejecutable
if exist "ejecutable\PDFImageConverter.exe" (
    echo 🚀 Ejecutable encontrado, iniciando...
    echo.
    start "" "ejecutable\PDFImageConverter.exe"
    exit /b 0
)

if exist "build\exe.win-amd64-3.13\PDFImageConverter.exe" (
    echo 🚀 Ejecutable encontrado (cx_Freeze), iniciando...
    echo.
    start "" "build\exe.win-amd64-3.13\PDFImageConverter.exe"
    exit /b 0
)

:: Si no hay ejecutable, ejecutar desde código fuente
echo 📋 No se encontró ejecutable, ejecutando desde código fuente...
echo.

:: Verificar dependencias básicas
echo 🔍 Verificando dependencias básicas...
C:/Python313/python.exe -c "import tkinter, PIL, PyPDF2, reportlab; print('✅ Dependencias básicas OK')" 2>nul
if errorlevel 1 (
    echo ❌ Faltan dependencias básicas
    echo.
    echo 💡 Instalando dependencias...
    C:/Python313/python.exe -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Error instalando dependencias
        pause
        exit /b 1
    )
)

:: Ejecutar la aplicación
echo 🚀 Iniciando aplicación MVC...
echo.
C:/Python313/python.exe main.py

if errorlevel 1 (
    echo.
    echo ❌ Error al ejecutar la aplicación
    echo.
    echo 💡 Puedes intentar:
    echo    1. build_executable.bat (para crear ejecutable)
    echo    2. Verificar que todas las dependencias estén instaladas
    echo.
    pause
) else (
    echo.
    echo 👋 Aplicación cerrada correctamente
)

timeout /t 3 >nul
