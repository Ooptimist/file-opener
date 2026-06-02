@echo off
setlocal
set "VSDEV=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat"
if not exist "%VSDEV%" (
  echo [ERROR] VsDevCmd.bat not found. Install Visual Studio Build Tools with C++ workload first.
  exit /b 1
)
call "%VSDEV%" -arch=x64 -host_arch=x64 >nul
set "PATH=%USERPROFILE%\.cargo\bin;%PATH%"
npm run tauri:build
