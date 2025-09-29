pipeline {
  agent any

  options {
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '15'))
    timeout(time: 120, unit: 'MINUTES') // primera vez puede tardar
  }

  parameters {
    string(name: 'BEHAVE_TAGS', defaultValue: '', description: 'Etiquetas Behave, ej: @smoke o @regression')
  }

  environment {
    // --- ANDROID SDK / AVD ---
    ANDROID_SDK_ROOT = "${WORKSPACE}\\android-sdk"
    ANDROID_AVD_HOME = "${WORKSPACE}\\.android\\avd"
    AVD_NAME         = "ci-pixel5-api30"
    API_LEVEL        = "30"
    SYSTEM_IMAGE     = "system-images;android-${API_LEVEL};google_apis;x86_64"
    DEVICE_PROFILE   = "pixel_5"

    // --- Appium / Python ---
    PYTHON           = "python"
    APPIUM_HOST      = "127.0.0.1"
    APPIUM_PORT      = "4723"
    APPIUM_BASE_PATH = "/wd/hub"

    // --- APK ---
    GDRIVE_REMOTE  = "gdrive"
    APK_DRIVE_PATH = "CI/medicenter_app.apk"
    APK_LOCAL_PATH = "app\\medicenter_app.apk"
    APP            = "app\\medicenter_app.apk"

    // --- Otros ---
    TZ = "America/Argentina/Buenos_Aires"
  }

  stages {

    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Verificar Java 17') {
      steps {
        bat '''
          setlocal
          if defined JAVA17_HOME (
            echo JAVA17_HOME=%JAVA17_HOME%
            "%JAVA17_HOME%\\bin\\java.exe" -version
          ) else (
            for /d %%D in ("C:\\Program Files\\Eclipse Adoptium\\jdk-17*") do set "JAVA17_HOME=%%D"
            if defined JAVA17_HOME (
              echo Detectado JAVA17_HOME=%JAVA17_HOME%
              "%JAVA17_HOME%\\bin\\java.exe" -version
            ) else (
              echo ERROR: No se encontro un JDK 17. Definilo como JAVA17_HOME o instala Temurin 17.
              exit /b 1
            )
          )
        '''
      }
    }

    stage('Android SDK & cmdline-tools (con JDK 17)') {
      options { timeout(time: 35, unit: 'MINUTES') }
      steps {
        bat '''
          setlocal ENABLEDELAYEDEXPANSION

          rem ==== Usar Java 17 para sdkmanager/avdmanager ====
          if not defined JAVA17_HOME for /d %%D in ("C:\\Program Files\\Eclipse Adoptium\\jdk-17*") do set "JAVA17_HOME=%%D"
          set "JAVA_HOME=%JAVA17_HOME%"
          set "PATH=%JAVA_HOME%\\bin;%PATH%"

          rem ==== Instalar commandline-tools si falta ====
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

          rem ==== Instalar paquetes del SDK ====
          set "PATH=%JAVA_HOME%\\bin;%ANDROID_SDK_ROOT%\\platform-tools;%ANDROID_SDK_ROOT%\\emulator;%ANDROID_SDK_ROOT%\\cmdline-tools\\latest\\bin;%PATH%"
          echo y | sdkmanager.bat --licenses
          echo y | sdkmanager.bat "platform-tools" "emulator" "platforms;android-%API_LEVEL%" "%SYSTEM_IMAGE%"
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

            if not exist "%USERPROFILE%\\.config\\rclone" mkdir "%USERPROFILE%\\.config\\rclone"
            powershell -NoProfile -Command "[IO.File]::WriteAllBytes('$env:USERPROFILE\\.config\\rclone\\rclone.conf',[Convert]::FromBase64String($env:RCLONE_CONF_B64))"

            if not exist "app" mkdir app
            "%RCLONE_CMD%" copyto "%GDRIVE_REMOTE%:%APK_DRIVE_PATH%" "%APK_LOCAL_PATH%" --progress

            if not exist "%APK_LOCAL_PATH%" ( echo ERROR: No se descargo la APK && exit /b 1 )
            dir "%APK_LOCAL_PATH%"
          '''
        }
      }
    }

    stage('Iniciar Emulador') {
      options { timeout(time: 20, unit: 'MINUTES') }
      steps {
        bat '''
          set "PATH=%ANDROID_SDK_ROOT%\\platform-tools;%ANDROID_SDK_ROOT%\\emulator;%PATH%"

          start /B "" "%ANDROID_SDK_ROOT%\\emulator\\emulator.exe" -avd "%AVD_NAME%" ^
            -no-window -no-boot-anim -gpu swiftshader_indirect -timezone "%TZ%" -no-snapshot -memory 3072 -netfast ^
            1> emulator.log 2>&1

          "%ANDROID_SDK_ROOT%\\platform-tools\\adb.exe" wait-for-device

          set BOOTED=
          for /L %%i in (1,1,120) do (
            for /f "usebackq tokens=* delims=" %%b in (`"%ANDROID_SDK_ROOT%\\platform-tools\\adb.exe" shell getprop sys.boot_completed 2^>NUL`) do set BOOTED=%%b
            if "%%BOOTED%%"=="1" goto :bootok
            timeout /t 5 >nul
          )
          :bootok

          "%ANDROID_SDK_ROOT%\\platform-tools\\adb.exe" shell input keyevent 82
          "%ANDROID_SDK_ROOT%\\platform-tools\\adb.exe" shell settings put global window_animation_scale 0
          "%ANDROID_SDK_ROOT%\\platform-tools\\adb.exe" shell settings put global transition_animation_scale 0
          "%ANDROID_SDK_ROOT%\\platform-tools\\adb.exe" shell settings put global animator_duration_scale 0

          if exist "%APP%" "%ANDROID_SDK_ROOT%\\platform-tools\\adb.exe" install -r "%APP%"
        '''
      }
    }

    stage('Appium + Dependencias Python') {
      options { timeout(time: 25, unit: 'MINUTES') }
      steps {
        bat '''
          where appium
          if %ERRORLEVEL% NEQ 0 (
            npm i -g appium appium-doctor
            appium driver install uiautomator2
          )
          appium-doctor --android

          start /B "" cmd /c "appium -a %APPIUM_HOST% -p %APPIUM_PORT% --base-path %APPIUM_BASE_PATH% --log appium.log 1> appium.out 2>&1"

          powershell -NoProfile -Command "$ErrorActionPreference='SilentlyContinue'; for($i=0;$i -lt 60;$i++){ try { iwr http://%APPIUM_HOST%:%APPIUM_PORT%%APPIUM_BASE_PATH%/status -UseBasicParsing | Out-Null; exit 0 } catch {}; Start-Sleep 2 }; exit 1"

          %PYTHON% -m venv .venv
          call .venv\\Scripts\\activate.bat
          python -m pip install -U pip wheel
          if exist requirements.txt ( pip install -r requirements.txt ) else ( pip install behave allure-behave appium-python-client selenium )
        '''
      }
    }

    stage('Ejecutar pruebas (Behave)') {
      steps {
        bat '''
          call .venv\\Scripts\\activate.bat
          if not exist "reports\\allure-results" mkdir "reports\\allure-results"

          set APPIUM_SERVER_URL=http://%APPIUM_HOST%:%APPIUM_PORT%%APPIUM_BASE_PATH%
          set ANDROID_AVD=%AVD_NAME%
          set ANDROID_API=%API_LEVEL%
          set APK_PATH=%APP%
          set TZ=%TZ%

          if not "%BEHAVE_TAGS%"=="" (
            behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results --tags "%BEHAVE_TAGS%"
          ) else (
            behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results
          )
        '''
      }
    }
  }

  post {
    always {
      script {
        if (env.WORKSPACE) {
          // no rompas el build si el cleanup falla
          bat(returnStatus: true, script: '''
            if exist "%ANDROID_SDK_ROOT%\\platform-tools\\adb.exe" (
              "%ANDROID_SDK_ROOT%\\platform-tools\\adb.exe" shell screencap -p /sdcard/final.png
              "%ANDROID_SDK_ROOT%\\platform-tools\\adb.exe" pull /sdcard/final.png "reports\\final.png" 2>nul
              "%ANDROID_SDK_ROOT%\\platform-tools\\adb.exe" emu kill 2>nul
            ) else (
              echo No hay adb (SDK fallido); omitiendo screencap y kill.
            )
            taskkill /F /IM node.exe /T 2>nul
          ''')
          archiveArtifacts artifacts: 'reports/**, appium.log, appium.out, emulator.log', fingerprint: true
          script {
            try { allure includeProperties: false, jdk: '', results: [[path: 'reports/allure-results']] } catch (ignored) { }
          }
        } else {
          echo 'Sin WORKSPACE (no se asignó nodo). Omitiendo cleanup/artefactos.'
        }
      }
    }
  }
}
