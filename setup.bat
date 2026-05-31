@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title VOID-TOOLS Setup

echo(
echo   VOID-TOOLS - Installation
echo   =========================
echo(

set "PYEXE="

if exist "%LocalAppData%\Programs\Python\Python313\python.exe" set "PYEXE=%LocalAppData%\Programs\Python\Python313\python.exe"
if not defined PYEXE if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PYEXE=%LocalAppData%\Programs\Python\Python312\python.exe"
if not defined PYEXE if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "PYEXE=%LocalAppData%\Programs\Python\Python311\python.exe"
if not defined PYEXE if exist "%LocalAppData%\Programs\Python\Python310\python.exe" set "PYEXE=%LocalAppData%\Programs\Python\Python310\python.exe"
if not defined PYEXE if exist "%LocalAppData%\Programs\Python\Python39\python.exe" set "PYEXE=%LocalAppData%\Programs\Python\Python39\python.exe"
if not defined PYEXE if exist "%LocalAppData%\Programs\Python\Python38\python.exe" set "PYEXE=%LocalAppData%\Programs\Python\Python38\python.exe"

where py >nul 2>&1
if not errorlevel 1 if not defined PYEXE for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PYEXE=%%P"
if not defined PYEXE (
  where py >nul 2>&1
  if not errorlevel 1 for /f "delims=" %%P in ('py -c "import sys; print(sys.executable)" 2^>nul') do set "PYEXE=%%P"
)

where python >nul 2>&1
if not defined PYEXE for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "PYEXE=%%P"

where python3 >nul 2>&1
if not defined PYEXE for /f "delims=" %%P in ('python3 -c "import sys; print(sys.executable)" 2^>nul') do set "PYEXE=%%P"

if not defined PYEXE (
  echo(
  echo   [ERREUR] Python introuvable.
  echo   Installe Python 3.8+ : https://www.python.org/downloads/
  echo   Coche "Add Python to PATH" puis relance setup.bat
  pause
  exit /b 1
)

"%PYEXE%" -c "import sys; sys.exit(0 if sys.version_info>=(3,8) else 1)" >nul 2>&1
if errorlevel 1 (
  echo   [ERREUR] Python 3.8 ou plus requis.
  "%PYEXE%" --version
  pause
  exit /b 1
)

if not exist "Void\main.py" (
  echo   [ERREUR] Dossier Void introuvable. Lance setup.bat depuis la racine du ZIP.
  pause
  exit /b 1
)

if not exist "Void\requirements.txt" (
  echo   [ERREUR] Void\requirements.txt introuvable.
  pause
  exit /b 1
)

if not exist "Void\data" mkdir "Void\data"
if not exist "Void\config" mkdir "Void\config"

echo   Python detecte :
"%PYEXE%" --version
echo(
echo   Mise a jour de pip...
"%PYEXE%" -m pip install --upgrade pip
if errorlevel 1 (
  echo   [ERREUR] pip introuvable ou mise a jour echouee.
  pause
  exit /b 1
)

echo(
echo   Installation des dependances...
"%PYEXE%" -m pip install -r "Void\requirements.txt"
if errorlevel 1 (
  echo(
  echo   [ERREUR] Installation echouee.
  pause
  exit /b 1
)

echo(
echo   OK - Dependances installees.
echo   Lance Void-Tools avec start.bat
echo(
pause
exit /b 0
