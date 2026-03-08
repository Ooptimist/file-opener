@echo off
chcp 65001 >nul
title FileOpener Build Tool
echo.
echo ============================================
echo    FileOpener - Build EXE
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python first.
    pause
    exit /b 1
)

echo [1/6] Python check passed...

REM Check PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [2/6] PyInstaller not found, installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] PyInstaller installation failed
        pause
        exit /b 1
    )
) else (
    echo [2/6] PyInstaller is installed...
)

REM Clean old build files
echo [3/6] Cleaning old build files...
if exist "build" (
    rmdir /s /q "build" 2>nul
    echo         Deleted build directory
)

REM Handle file lock
echo [4/6] Checking file lock...
set FILE_LOCKED=0

if exist "dist\FileOpener.exe" (
    echo         Found old EXE file
    
    REM Try to close running program
    taskkill /f /im FileOpener.exe >nul 2>&1
    if not errorlevel 1 (
        echo         Closed running FileOpener.exe
        timeout /t 2 /nobreak >nul
    )
    
    REM Try to delete file
    del /f /q "dist\FileOpener.exe" >nul 2>&1
    
    if exist "dist\FileOpener.exe" (
        echo [WARN] File locked, trying to rename...
        
        REM Delete old backup
        if exist "dist\FileOpener_old.exe" (
            del /f /q "dist\FileOpener_old.exe" >nul 2>&1
        )
        
        REM Rename
        ren "dist\FileOpener.exe" "FileOpener_old.exe" >nul 2>&1
        
        if exist "dist\FileOpener.exe" (
            echo [ERROR] Cannot handle old file. Please close the program manually.
            echo.
            echo Steps:
            echo 1. Open Task Manager
            echo 2. End FileOpener.exe process
            echo 3. Run build.bat again
            pause
            exit /b 1
        ) else (
            echo         Renamed to FileOpener_old.exe
            set FILE_LOCKED=1
        )
    ) else (
        echo         Deleted old EXE file
    )
) else (
    echo         No old file to clean
)

REM Build
echo [5/6] Starting build...
echo.

python -m PyInstaller --clean --noconfirm FileOpener.spec

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    echo.
    echo Possible reasons:
    echo 1. FileOpener.exe is running
    echo 2. Missing dependencies
    echo 3. Permission denied
    echo.
    pause
    exit /b 1
)

echo.
echo [6/6] Build complete!
echo.

REM Check output file
if exist "dist\FileOpener.exe" (
    echo ============================================
    echo [SUCCESS] EXE file generated!
    echo ============================================
    echo.
    echo File info:
    dir "dist\FileOpener.exe" | findstr "FileOpener.exe"
    echo.
    
    REM Clean backup
    if exist "dist\FileOpener_old.exe" (
        del /f /q "dist\FileOpener_old.exe" >nul 2>&1
        if not errorlevel 1 (
            echo [CLEAN] Deleted backup file
        )
    )
    
    if %FILE_LOCKED%==1 (
        echo.
        echo [NOTE] Old file was locked, new file generated.
        echo         If new file doesn't work, please restart and try again.
    )
    
    echo.
    echo Press any key to open output folder...
    pause >nul
    explorer "dist"
) else (
    echo [ERROR] EXE file not found!
    echo.
    echo Check build\FileOpener\warn-FileOpener.txt for details
    pause
)
