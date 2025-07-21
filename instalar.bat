@echo off
title PDF Image Converter - Instalador Completo
echo.
echo 📦 ================================================
echo    PDF Image Converter - Instalador Completo
echo ================================================
echo.
echo 🎯 Este script instalará y configurará la aplicación
echo.

cd /d "%~dp0"

:: Verificar Python
echo 🔍 Paso 1: Verificando Python...
C:/Python313/python.exe --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado
    echo.
    echo 💡 Por favor instala Python 3.7+ desde:
    echo    https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

C:/Python313/python.exe --version
echo ✅ Python encontrado
echo.

:: Instalar dependencias
echo 🔧 Paso 2: Instalando dependencias...
C:/Python313/python.exe -m pip install --upgrade pip
C:/Python313/python.exe -m pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Error instalando dependencias
    echo.
    echo 💡 Intenta ejecutar manualmente:
    echo    pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo ✅ Dependencias instaladas
echo.

:: Crear icono
echo 🎨 Paso 3: Creando icono...
if not exist "icon.ico" (
    C:/Python313/python.exe create_icon.py
)
echo ✅ Icono creado
echo.

:: Probar aplicación
echo 🧪 Paso 4: Probando aplicación...
echo Ejecutando verificación de dependencias...
C:/Python313/python.exe -c "from src.utils.dependency_checker import DependencyChecker; checker = DependencyChecker(); can_run, report = checker.check_and_show_report(); print('✅ Verificación completada' if can_run else '❌ Hay problemas')"

if errorlevel 1 (
    echo ❌ Error en la verificación
    pause
    exit /b 1
)

echo.
echo 🏗️ Paso 5: ¿Quieres crear un ejecutable? (s/n)
set /p create_exe="Respuesta: "

if /i "%create_exe%"=="s" (
    echo.
    echo 🔨 Creando ejecutable...
    call build_executable.bat
)

echo.
echo 🎉 ================================================
echo    ¡Instalación Completada!
echo ================================================
echo.
echo 📋 Archivos disponibles:
echo    • main.py - Ejecutar desde código fuente
echo    • iniciar_app.bat - Script de inicio automático
echo    • build_executable.bat - Crear ejecutable

if exist "ejecutable\PDFImageConverter.exe" (
    echo    • ejecutable\PDFImageConverter.exe - Ejecutable listo
)

echo.
echo 🚀 Para usar la aplicación:
echo    1. Doble clic en iniciar_app.bat
echo    2. O ejecutar: python main.py
if exist "ejecutable\PDFImageConverter.exe" (
    echo    3. O usar el ejecutable en la carpeta 'ejecutable'
)

echo.
echo 📚 Documentación:
echo    • README_MVC.md - Guía completa
echo    • app_config.json - Configuraciones
echo.
echo ✅ ¡Todo listo para usar!
echo.
pause
