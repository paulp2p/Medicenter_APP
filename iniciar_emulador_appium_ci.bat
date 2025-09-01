@echo off
SETLOCAL

rem ================== RUTAS Y VARIABLES ==================
set PROJECT_DIR=C:\Users\paulr\SILTIUM\Medicenter_APP
set VENV_DIR=%PROJECT_DIR%\venv
set SDK_PATH=%LOCALAPPDATA%\Android\Sdk

rem APK y AVD
set APK_PATH=%PROJECT_DIR%\apk\medicenter_app.apk
set AVD_NAME=medicenter_avd

rem Puertos/URLs
set MOCK_HOST=0.0.0.0
set MOCK_PORT=8081
set MOCK_URL=http://127.0.0.1:%MOCK_PORT%

rem Appium (puede ser solo "appium" si ya está en PATH)
set APPIUM_CMD=appium

echo ============================================
echo  Iniciando emulador, Appium y Mock SMS...
echo ============================================
echo.

rem ================== 1) MOCK SMS ==================
echo Iniciando Mock SMS en %MOCK_URL% ...
start "Mock SMS" cmd /k "cd /d %PROJECT_DIR% && call %VENV_DIR%\Scripts\activate.bat && python -m uvicorn mock_sms:app --host %MOCK_HOST% --port %MOCK_PORT%"

rem ================== 2) EMULADOR ==================
echo Iniciando emulador %AVD_NAME%...
start "Emulator" "%SDK_PATH%\emulator\emulator.exe" -avd %AVD_NAME% -no-boot-anim -no-snapshot -no-audio -camera-back none -camera-front none -gpu swiftshader_indirect -netfast -accel on

echo Esperando a que el emulador se conecte...
:wait_for_device
"%SDK_PATH%\platform-tools\adb.exe" get-state | findstr /C:"device" >nul
IF ERRORLEVEL 1 (
    timeout /t 2 >nul
    goto wait_for_device
)
echo Emulador conectado.

"%SDK_PATH%\platform-tools\adb.exe" wait-for-device

:check_boot
"%SDK_PATH%\platform-tools\adb.exe" shell getprop sys.boot_completed | findstr "1" >nul
IF ERRORLEVEL 1 (
    timeout /t 2 >nul
    goto check_boot
)
echo Android ha arrancado completamente.

echo Desactivando animaciones...
"%SDK_PATH%\platform-tools\adb.exe" shell settings put global window_animation_scale 0
"%SDK_PATH%\platform-tools\adb.exe" shell settings put global transition_animation_scale 0
"%SDK_PATH%\platform-tools\adb.exe" shell settings put global animator_duration_scale 0

echo Instalando APK (si cambia, se re-instala)...
"%SDK_PATH%\platform-tools\adb.exe" install -r "%APK_PATH%"

rem ================== 3) APPIUM ==================
echo Iniciando servidor Appium...
start "Appium" cmd /k "%APPIUM_CMD%"

timeout /t 5 >nul

echo ============================================
echo  Todo listo. Mock SMS, Emulador y Appium en marcha.
echo  Mock URL: %MOCK_URL%
echo ============================================

ENDLOCAL
