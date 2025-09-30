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
          rem --- PATH base para Appium / SDK ---
          set "JAVA_HOME=%JAVA17_HOME%"
          set "ANDROID_HOME=%ANDROID_SDK_ROOT%"
          set "PATH=%JAVA_HOME%\\bin;%ANDROID_SDK_ROOT%\\platform-tools;%ANDROID_SDK_ROOT%\\emulator;%PATH%"

          rem Asegurar binarios globales de npm en PATH
          set "NPM_PREFIX=%APPDATA%\\npm"
          if exist "%NPM_PREFIX%" set "PATH=%NPM_PREFIX%;%PATH%"

          where node || (echo ERROR: Node.js/NPM no estan en PATH & exit /b 1)

          rem Instalar Appium + doctor si no existen
          where appium >nul 2>&1
          if %ERRORLEVEL% NEQ 0 (
            npm i -g appium @appium/doctor
            if exist "%APPDATA%\\npm" set "PATH=%APPDATA%\\npm;%PATH%"
          )

          rem Doctor (no fallar si hay warnings)
          cmd /c appium-doctor --android  || echo (appium-doctor devolvio warnings; continuo)

          rem Levantar Appium y esperar /status
          start /B "" cmd /c "appium -a %APPIUM_HOST% -p %APPIUM_PORT% --base-path %APPIUM_BASE_PATH% --log appium.log 1> appium.out 2>&1"
          powershell -NoProfile -Command "$ErrorActionPreference='SilentlyContinue'; for($i=0;$i -lt 60;$i++){ try { iwr http://%APPIUM_HOST%:%APPIUM_PORT%%APPIUM_BASE_PATH%/status -UseBasicParsing | Out-Null; exit 0 } catch {}; Start-Sleep 2 }; exit 1"

          rem ---- Python local al workspace (instalar si no hay) ----
          set "PY_EXE=%SystemRoot%\\py.exe"
          set "PY_LOCAL=%WORKSPACE%\\.tools\\Python311\\python.exe"

          if exist "%PY_EXE%" (
            "%PY_EXE%" -3 -c "import sys" 1>nul 2>nul || set "USE_LOCAL=1"
          ) else (
            set "USE_LOCAL=1"
          )

          if "%USE_LOCAL%"=="1" (
            if not exist "%WORKSPACE%\\.tools" mkdir "%WORKSPACE%\\.tools"
            if not exist "%PY_LOCAL%" (
              powershell -NoProfile -Command "$u='https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe'; $d='$env:WORKSPACE\\.tools\\py311.exe'; iwr $u -OutFile $d"
              start /wait "" "%WORKSPACE%\\.tools\\py311.exe" /quiet InstallAllUsers=0 PrependPath=0 Include_launcher=0 Include_test=0 TargetDir="%WORKSPACE%\\.tools\\Python311"
            )
            set "PYTHON_BOOT=%PY_LOCAL%"
          ) else (
            set "PYTHON_BOOT=%PY_EXE% -3"
          )

          rem Crear venv y deps con el Python elegido
          if exist ".venv\\Scripts\\python.exe" del /q ".venv\\Scripts\\python.exe" >nul 2>&1
          %PYTHON_BOOT% -m venv .venv
          if not exist ".venv\\Scripts\\activate.bat" ( echo ERROR: No se creo la venv & exit /b 1 )

          set "VENV_PY=.venv\\Scripts\\python.exe"
          call .venv\\Scripts\\activate.bat
          "%VENV_PY%" -m pip install -U pip wheel
          if exist requirements.txt (
            "%VENV_PY%" -m pip install -r requirements.txt
          ) else (
            "%VENV_PY%" -m pip install behave allure-behave appium-python-client selenium
          )
        '''
      }
    }

    stage('Ejecutar pruebas (Behave)') {
      steps {
        bat '''
          if not exist ".venv\\Scripts\\activate.bat" (
            echo ERROR: no hay venv; revisa el stage anterior & exit /b 1
          )
          call .venv\\Scripts\\activate.bat
          set "VENV_PY=.venv\\Scripts\\python.exe"

          if not exist "reports\\allure-results" mkdir "reports\\allure-results"

          set APPIUM_SERVER_URL=http://%APPIUM_HOST%:%APPIUM_PORT%%APPIUM_BASE_PATH%
          set ANDROID_AVD=%AVD_NAME%
          set ANDROID_API=%API_LEVEL%
          set APK_PATH=%APP%
          set TZ=%TZ%

          if not "%BEHAVE_TAGS%"=="" (
            "%VENV_PY%" -m behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results --tags "%BEHAVE_TAGS%"
          ) else (
            "%VENV_PY%" -m behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results
          )
        '''
      }
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
}
