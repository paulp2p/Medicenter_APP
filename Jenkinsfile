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

    // --- Appium / Python ---
    PYTHON           = "py -3" // <-- ahora es SOLO el intérprete
    // Fallbacks (no se usan aquí directo; se resuelven en cada stage)
    PY_SYS_PY312     = "C:\\Program Files\\Python312\\python.exe"
    PY_USER_PY312    = "C:\\Users\\paulr\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" // <-- ajusta si tu usuario es otro
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

            if not exist "%APK_LOCAL_PATH%" ( echo ERROR:
