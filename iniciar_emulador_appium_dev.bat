@echo off
SETLOCAL

:: Ruta del SDK
set SDK_PATH=C:\Users\paulr\AppData\Local\Android\Sdk

:: Ruta de la APK
set APK_PATH=C:\Users\paulr\SILTIUM\Medicenter_APP\apk\medicenter_app.apk

:: Nombre del AVD
set AVD_NAME=medicenter_avd

echo ============================================
echo  Iniciando emulador y Appium en STAGING...
echo ============================================
echo.

:: Iniciar emulador con optimizaciones
echo Iniciando emulador %AVD_NAME%...
start "" "%SDK_PATH%\emulator\emulator.exe" -avd %AVD_NAME% -no-boot-anim -no-snapshot -no-audio -camera-back none -camera-front none -gpu swiftshader_indirect -netfast -accel on

:: Esperar a que el emulador esté conectado
echo Esperando a que el emulador se conecte...
:wait_for_device
%SDK_PATH%\platform-tools\adb.exe get-state | findstr /C:"device" >nul
IF ERRORLEVEL 1 (
    timeout /t 2 >nul
    goto wait_for_device
)

echo Emulador conectado.

:: Esperar a que el sistema Android termine de arrancar
%SDK_PATH%\platform-tools\adb.exe wait-for-device

:check_boot
%SDK_PATH%\platform-tools\adb.exe shell getprop sys.boot_completed | findstr "1" >nul
IF ERRORLEVEL 1 (
    timeout /t 2 >nul
    goto check_boot
)

echo Android ha arrancado completamente.

:: Desactivar animaciones para mejorar velocidad
echo Desactivando animaciones...
%SDK_PATH%\platform-tools\adb.exe shell settings put global window_animation_scale 0
%SDK_PATH%\platform-tools\adb.exe shell settings put global transition_animation_scale 0
%SDK_PATH%\platform-tools\adb.exe shell settings put global animator_duration_scale 0

:: Instalar APK
echo Instalando APK...
%SDK_PATH%\platform-tools\adb.exe install -r "%APK_PATH%"

:: Iniciar servidor Appium
echo Iniciando servidor Appium...
start "" cmd /k appium

:: Esperar unos segundos para que Appium termine de inicializar
timeout /t 5 >nul

echo ============================================
echo  Todo listo. Emulador y Appium en marcha.
echo ============================================

:: Pausa final (solo en desarrollo)
pause

ENDLOCAL
