pipeline {
  agent any

  options {
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '15'))
    timeout(time: 120, unit: 'MINUTES')
  }

  parameters {
    string(name: 'BEHAVE_TAGS', defaultValue: '', description: 'Etiquetas Behave, ej.: @smoke')
  }

  environment {
    // --- Android SDK / AVD ---
    ANDROID_SDK_ROOT = "${WORKSPACE}\\android-sdk"
    ANDROID_HOME     = "${WORKSPACE}\\android-sdk"
    ANDROID_AVD_HOME = "${WORKSPACE}\\.android\\avd"
    AVD_NAME         = "ci-pixel5-api30"
    API_LEVEL        = "30"
    SYSTEM_IMAGE     = "system-images;android-${API_LEVEL};google_apis;x86_64"
    DEVICE_PROFILE   = "pixel_5"

    // --- Appium / Node ---
    APPIUM_HOST      = "127.0.0.1"
    APPIUM_PORT      = "4723"
    APPIUM_BASE_PATH = "/wd/hub"

    // --- APK (Google Drive con rclone) ---
    GDRIVE_REMOTE  = "gdrive"
    APK_DRIVE_PATH = "CI/medicenter_app.apk"
    APK_LOCAL_PATH = "app\\medicenter_app.apk"
    APP            = "app\\medicenter_app.apk"

    // --- Zona horaria ---
    TZ = "America/Argentina/Buenos_Aires"
  }

  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Verificar Java 17') {
      steps {
        bat '''
          setlocal
          if not defined JAVA17_HOME (
            for /d %%D in ("C:\\Program Files\\Eclipse Adoptium\\jdk-17*") do set "JAVA17_HOME=%%D"
          )
          if not defined JAVA17_HOME (
            echo ERROR: No se encontro un JDK 17. Define JAVA17_HOME o instala Temurin 17.
            exit /b 1
          )
          echo JAVA17_HOME=%JAVA17_HOME%
          "%JAVA17_HOME%\\bin\\java.exe" -version
        '''
      }
    }

    stage('Android SDK & cmdline-tools (con JDK 17)') {
      options { timeout(time: 35, unit: 'MINUTES') }
      steps {
        bat '''
          setlocal ENABLEDELAYEDEXPANSION
          set "JAVA_HOME=%JAVA17_HOME%"
          set "PATH=%JAVA_HOME%\\bin;%PATH%"

          if not exist "%ANDROID_SDK_ROOT%\\cmdline-tools" mkdir "%ANDROID_SDK_ROOT%\\cmdline-tools"
          if not exist "%ANDROID_SDK_ROOT%\\cmdline-tools\\latest\\bin\\sdkmanager.bat" (
            cd /d "%ANDROID_SDK_ROOT%\\cmdline-tools"
            curl -L -o cmdtools.zip https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip
            powershell -NoProfile -Command "Expand-Archive -Force cmdtools.zip ."
            del cmdtools.zip
            if exist "%ANDROID_SDK_ROOT%\\cmdline-tools\\cmdline-tools" (
              move "%ANDROID_SDK_ROOT%\\cmdline-tools\\cmdline-tools" "%ANDROID_SDK_ROOT%\\cmdline-tools\\latest" >nul
            )
          )

          set "PATH=%JAVA_HOME%\\bin;%ANDROID_SDK_ROOT%\\platform-tools;%ANDROID_SDK_ROOT%\\emulator;%ANDROID_SDK_ROOT%\\cmdline-tools\\latest\\bin;%PATH%"

          ( for /L %%n in (1,1,400) do @echo y ) | sdkmanager.bat --licenses
          ( for /L %%n in (1,1,400) do @echo y ) | sdkmanager.bat "platform-tools" "emulator" "platforms;android-%API_LEVEL%" "%SYSTEM_IMAGE%"
        '''
      }
    }

    stage('Crear AVD (si no existe)') {
      steps {
        bat '''
          set "JAVA_HOME=%JAVA17_HOME%"
          set "PATH=%JAVA_HOME%\\bin;%ANDROID_SDK_ROOT%\\platform-tools;%ANDROID_SDK_ROOT%\\emulator;%ANDROID_SDK_ROOT%\\cmdline-tools\\latest\\bin;%PATH%"

          for /f "tokens=*" %%A in ('avdmanager.bat list avd ^| findstr /C:"Name: %AVD_NAME%"') do set FOUND=1
          if not defined FOUND (
            echo no | avdmanager.bat create avd -n "%AVD_NAME%" -k "%SYSTEM_IMAGE%" --device "%DEVICE_PROFILE%" --sdcard 2048M
          )
        '''
      }
    }

    stage('Fetch APK (rclone desde Drive)') {
      steps {
        withCredentials([string(credentialsId: 'RCLONE_CONF_B64', variable: 'RCLONE_CONF_B64')]) {
          bat '''
            if not exist ".tools" mkdir .tools
            if not exist ".tools\\rclone.exe" (
              curl -L -o rclone.zip https://downloads.rclone.org/rclone-current-windows-amd64.zip
              powershell -NoProfile -Command "Expand-Archive -Force rclone.zip .tools\\rclone_zip"
              for /r ".tools\\rclone_zip" %%F in (rclone.exe) do copy "%%F" ".tools\\rclone.exe" >nul
              rmdir /s /q ".tools\\rclone_zip"
              del rclone.zip
            )
            set "RCLONE_CMD=%CD%\\.tools\\rclone.exe"

            if not exist "%APPDATA%\\rclone" mkdir "%APPDATA%\\rclone"
            powershell -NoProfile -Command "[IO.File]::WriteAllBytes($env:APPDATA+'\\rclone\\rclone.conf',[Convert]::FromBase64String($env:RCLONE_CONF_B64))"
            set "RCLONE_CONF=%APPDATA%\\rclone\\rclone.conf"

            if not exist "app" mkdir app
            "%RCLONE_CMD%" --config "%RCLONE_CONF%" copyto "%GDRIVE_REMOTE%:%APK_DRIVE_PATH%" "%APK_LOCAL_PATH%" --progress
            if not exist "%APK_LOCAL_PATH%" ( echo ERROR: No se descargo la APK && exit /b 1 )
          '''
        }
      }
    }

    stage('Iniciar Emulador') {
      options { timeout(time: 25, unit: 'MINUTES') }
      steps {
        bat '''
          setlocal ENABLEDELAYEDEXPANSION
          set "ADB=%ANDROID_SDK_ROOT%\\platform-tools\\adb.exe"
          set "EMU=%ANDROID_SDK_ROOT%\\emulator\\emulator.exe"
          set "PATH=%ANDROID_SDK_ROOT%\\platform-tools;%ANDROID_SDK_ROOT%\\emulator;%PATH%"

          start /B "" "%EMU%" -avd "%AVD_NAME%" ^
            -no-window -no-boot-anim -gpu swiftshader_indirect -timezone "%TZ%" -no-snapshot -memory 3072 -netfast ^
            1> emulator.log 2>&1

          "%ADB%" wait-for-device

          set BOOT=
          set DEV=
          for /L %%i in (1,1,180) do (
            set BOOT=
            set DEV=
            for /f "usebackq delims=" %%b in (`"%ADB%" shell getprop sys.boot_completed 2^>NUL`) do set BOOT=%%b
            for /f "usebackq delims=" %%b in (`"%ADB%" shell getprop dev.bootcomplete 2^>NUL`) do set DEV=%%b
            if "!BOOT!"=="1" if "!DEV!"=="1" (
              "%ADB%" shell pm list packages 1>nul 2>&1
              if !ERRORLEVEL! EQU 0 goto :pm_ready
            )
            timeout /t 3 >nul
          )
          :pm_ready

          "%ADB%" shell input keyevent 82
          "%ADB%" shell settings put global window_animation_scale 0
          "%ADB%" shell settings put global transition_animation_scale 0
          "%ADB%" shell settings put global animator_duration_scale 0

          if exist "%APP%" "%ADB%" install -r "%APP%"
        '''
      }
    }

    stage('Appium + Dependencias Python') {
      options { timeout(time: 25, unit: 'MINUTES') }
      steps {
        bat '''
          setlocal ENABLEDELAYEDEXPANSION

          rem --- PATH base para Appium / SDK ---
          set "JAVA_HOME=%JAVA17_HOME%"
          set "ANDROID_HOME=%ANDROID_SDK_ROOT%"
          set "PATH=%JAVA_HOME%\\bin;%ANDROID_SDK_ROOT%\\platform-tools;%ANDROID_SDK_ROOT%\\emulator;%PATH%"

          rem --- Binarios globales de npm en PATH (cuenta del servicio Jenkins) ---
          set "NPM_PREFIX=%APPDATA%\\npm"
          if exist "%NPM_PREFIX%" set "PATH=%NPM_PREFIX%;%PATH%"

          where node || (echo ERROR: Node.js/NPM no estan en PATH & exit /b 1)

          rem --- Appium + doctor (si falta, instalar) ---
          where appium >nul 2>&1
          if %ERRORLEVEL% NEQ 0 (
            npm i -g appium @appium/doctor
            if exist "%APPDATA%\\npm" set "PATH=%APPDATA%\\npm;%PATH%"
          )

          rem --- Doctor (no fallar por warnings; 'android' tool ya no existe) ---
          cmd /c appium-doctor --android  || echo (appium-doctor devolvio warnings; continuo)

          rem --- Levantar Appium y esperar /status ---
          start /B "" cmd /c "appium -a %APPIUM_HOST% -p %APPIUM_PORT% --base-path %APPIUM_BASE_PATH% --log appium.log 1> appium.out 2>&1"
          powershell -NoProfile -Command "$ErrorActionPreference='SilentlyContinue'; for($i=0;$i -lt 60;$i++){ try { iwr http://%APPIUM_HOST%:%APPIUM_PORT%%APPIUM_BASE_PATH%/status -UseBasicParsing | Out-Null; exit 0 } catch {}; Start-Sleep 2 }; exit 1"

          rem ================= PYTHON LOCAL (portable) =================
          set "PY_EXE=%SystemRoot%\\py.exe"
          set "PY_DIR=%WORKSPACE%\\.tools\\Python311"
          set "PY_LOCAL=%PY_DIR%\\python.exe"
          set "PY_DL=%WORKSPACE%\\.tools\\py311.exe"

          rem Si py.exe no tiene un 3.x visible para el usuario del servicio, usamos portable
          if exist "%PY_EXE%" (
            "%PY_EXE%" -3 -c "import sys" 1>nul 2>nul || set "USE_LOCAL=1"
          ) else (
            set "USE_LOCAL=1"
          )

          if "%USE_LOCAL%"=="1" (
            if not exist "%WORKSPACE%\\.tools" mkdir "%WORKSPACE%\\.tools"
            if not exist "%PY_LOCAL%" (
              echo Descargando Python 3.11 portable en "%PY_DL%"...
              curl -L -o "%PY_DL%" https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
              if not exist "%PY_DL%" (echo ERROR: No se pudo descargar Python & exit /b 1)

              echo Instalando Python 3.11 portable en "%PY_DIR%"...
              start /wait "" "%PY_DL%" /quiet InstallAllUsers=0 PrependPath=0 Include_launcher=0 Include_test=0 Include_pip=1 TargetDir="%PY_DIR%"

              rem Espera hasta 180s a que aparezca python.exe (algunos instaladores spawnean msiexec)
              set /a __T=0
              :__WAIT_PY
              if exist "%PY_LOCAL%" goto __PY_OK
              set /a __T+=1
              if !__T! GEQ 180 goto __PY_FALLBACK_EMBED
              timeout /t 1 >nul
              goto __WAIT_PY

              :__PY_OK
              echo Python instalado: %PY_LOCAL%
              set "PYTHON_BOOT=%PY_LOCAL%"
              goto __HAVE_PY

              :__PY_FALLBACK_EMBED
              echo WARNING: python.exe no aparecio tras instalar; usando fallback embebido...
              set "EMB_DIR=%WORKSPACE%\\.tools\\Python311-embed"
              set "EMB_ZIP=%WORKSPACE%\\.tools\\py311-embed.zip"
              curl -L -o "%EMB_ZIP%" https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip
              if not exist "%EMB_ZIP%" (echo ERROR: No se pudo descargar Python embebido & exit /b 1)
              powershell -NoProfile -Command "Expand-Archive -Force '%EMB_ZIP%' '%EMB_DIR%'"
              del "%EMB_ZIP%"

              rem Habilitar 'import site' en el embebido
              powershell -NoProfile -Command "(Get-Content '%EMB_DIR%\\python311._pth') -replace '^(#\\s*)?import site','import site' | Set-Content '%EMB_DIR%\\python311._pth'"

              set "PYTHON_BOOT=%EMB_DIR%\\python.exe"

              rem Bootstrap pip en el embebido
              curl -L -o "%WORKSPACE%\\.tools\\get-pip.py" https://bootstrap.pypa.io/get-pip.py
              "%PYTHON_BOOT%" "%WORKSPACE%\\.tools\\get-pip.py"
              del "%WORKSPACE%\\.tools\\get-pip.py"

              rem Marcador para etapa de pruebas (sin venv)
              > py_mode.env echo PY_NO_VENV=1
            ) else (
              set "PYTHON_BOOT=%PY_LOCAL%"
            )
          ) else (
            set "PYTHON_BOOT=%PY_EXE% -3"
          )

          :__HAVE_PY
          echo Usando interprete: %PYTHON_BOOT%

          rem --- Intentar venv; si falla (embebido), seguimos sin venv ---
          %PYTHON_BOOT% -m venv .venv 1>nul 2>nul

          if exist ".venv\\Scripts\\python.exe" (
            call .venv\\Scripts\\activate.bat
            set "VENV_PY=.venv\\Scripts\\python.exe"
            "%VENV_PY%" -m pip install -U pip wheel
            if exist requirements.txt (
              "%VENV_PY%" -m pip install -r requirements.txt
            ) else (
              "%VENV_PY%" -m pip install behave allure-behave appium-python-client selenium
            )
          ) else (
            echo WARNING: venv no disponible; instalando deps en el Python portable...
            %PYTHON_BOOT% -m pip install -U pip wheel
            if exist requirements.txt (
              %PYTHON_BOOT% -m pip install -r requirements.txt
            ) else (
              %PYTHON_BOOT% -m pip install behave allure-behave appium-python-client selenium
            )
            > py_mode.env echo PY_NO_VENV=1
          )
        '''
      }
    }

    stage('Ejecutar pruebas (Behave)') {
      steps {
        bat '''
          setlocal
          set "APPIUM_SERVER_URL=http://%APPIUM_HOST%:%APPIUM_PORT%%APPIUM_BASE_PATH%"
          set "ANDROID_AVD=%AVD_NAME%"
          set "ANDROID_API=%API_LEVEL%"
          set "APK_PATH=%APP%"
          set "TZ=%TZ%"

          if exist py_mode.env (
            for /f "usebackq delims=" %%L in (`type py_mode.env`) do set %%L
          )

          if exist ".venv\\Scripts\\activate.bat" (
            call .venv\\Scripts\\activate.bat
            set "RUNPY=python"
          ) else (
            rem usar Python portable directo
            if exist "%WORKSPACE%\\.tools\\Python311\\python.exe" (
              set "RUNPY=%WORKSPACE%\\.tools\\Python311\\python.exe"
            ) else (
              set "RUNPY=%WORKSPACE%\\.tools\\Python311-embed\\python.exe"
            )
          )

          if not exist "reports\\allure-results" mkdir "reports\\allure-results"

          if not "%BEHAVE_TAGS%"=="" (
            %RUNPY% -m behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results --tags "%BEHAVE_TAGS%"
          ) else (
            %RUNPY% -m behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results
          )
        '''
      }
    }


  post {
    always {
      bat(returnStatus: true, script: """
        if exist "%ANDROID_SDK_ROOT%\\platform-tools\\adb.exe" "%ANDROID_SDK_ROOT%\\platform-tools\\adb.exe" shell screencap -p /sdcard/final.png
        if exist "%ANDROID_SDK_ROOT%\\platform-tools\\adb.exe" "%ANDROID_SDK_ROOT%\\platform-tools\\adb.exe" pull /sdcard/final.png "reports\\final.png" 2>nul
        if exist "%ANDROID_SDK_ROOT%\\platform-tools\\adb.exe" "%ANDROID_SDK_ROOT%\\platform-tools\\adb.exe" emu kill 2>nul
        taskkill /F /IM node.exe /T 2>nul
      """)
      archiveArtifacts artifacts: 'reports/**, appium.log, appium.out, emulator.log', fingerprint: true
    }
  }

