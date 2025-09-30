pipeline {
  agent { label 'android && linux' }   // Ajusta a la(s) etiqueta(s) de tu nodo

  options {
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '15'))
    timeout(time: 120, unit: 'MINUTES')
  }

  parameters {
    string(name: 'BEHAVE_TAGS', defaultValue: '', description: 'Etiquetas Behave, ej.: @smoke')
    string(name: 'APK_GDRIVE_PATH', defaultValue: 'Medicenter/apks/medicenter_app.apk', description: 'Ruta en Google Drive (remoto rclone) al APK')
    string(name: 'APK_LOCAL_NAME',  defaultValue: 'medicenter_app.apk', description: 'Nombre local del APK en el workspace')
  }

  environment {
    // Android SDK (ya instalados en el nodo por el bootstrap)
    ANDROID_HOME     = "${HOME}/android-sdk"
    ANDROID_SDK_ROOT = "${HOME}/android-sdk"
    ANDROID_AVD_HOME = "${HOME}/.android/avd"

    // AVD preparado en el nodo (del bootstrap)
    AVD_NAME       = "ci-pixel5-api30"

    // Appium local
    APPIUM_HOST    = "127.0.0.1"
    APPIUM_PORT    = "4723"

    // Rclone
    RCLONE_REMOTE  = "gdrive"   // nombre del remoto en tu rclone.conf

    // Reportes
    REPORTS        = "${WORKSPACE}/reports"
    // Expone ruta del APK para que tu framework/capabilities lo use si corresponde
    APK_PATH       = "${WORKSPACE}/${params.APK_LOCAL_NAME}"
  }

  stages {

    stage('Preparar carpetas') {
      steps {
        sh '''
          set -euxo pipefail
          mkdir -p "$REPORTS/allure-results"
        '''
      }
    }

    stage('Fetch APK desde Google Drive') {
      steps {
        withCredentials([string(credentialsId: 'RCLONE_CONF_B64', variable: 'RCLONE_CONF_B64')]) {
          sh '''
            set -euxo pipefail
            mkdir -p "$HOME/.config/rclone"
            echo "$RCLONE_CONF_B64" | base64 -d > "$HOME/.config/rclone/rclone.conf"
            chmod 600 "$HOME/.config/rclone/rclone.conf"

            # Descarga y renombra al nombre esperado
            rclone copy "$RCLONE_REMOTE:${APK_GDRIVE_PATH}" .
            FOUND="$(basename "${APK_GDRIVE_PATH}")"
            mv -f "$FOUND" "${APK_LOCAL_NAME}"

            # Chequeo tamaño mínimo (5 MB)
            [ "$(stat -c%s "${APK_LOCAL_NAME}")" -gt 5242880 ]
          '''
        }
      }
    }

    stage('Python: venv + deps') {
      steps {
        sh '''
          set -euxo pipefail
          python3 -m venv .venv
          . .venv/bin/activate
          python -m pip install --upgrade pip wheel setuptools
          if [ -f requirements.txt ]; then
            python -m pip install -r requirements.txt
          else
            python -m pip install behave allure-behave appium-python-client selenium
          fi
        '''
      }
    }

    stage('Iniciar Appium') {
      steps {
        sh '''
          set -euxo pipefail
          # Lanza appium en background
          nohup npx appium --address "$APPIUM_HOST" --port "$APPIUM_PORT" > appium.log 2>&1 &
          # Espera /status (máx ~120s)
          for i in $(seq 1 60); do
            curl -sf "http://$APPIUM_HOST:$APPIUM_PORT/status" >/dev/null && exit 0 || true
            sleep 2
          done
          echo "Appium no respondió a tiempo" >&2
          exit 1
        '''
      }
    }

    stage('Iniciar emulador') {
      steps {
        sh '''
          set -euxo pipefail
          ADB="$ANDROID_SDK_ROOT/platform-tools/adb"
          EMU="$ANDROID_SDK_ROOT/emulator/emulator"
          [ -x "$EMU" ] || { echo "[ERROR] No existe $EMU"; exit 114; }
          [ -x "$ADB" ] || { echo "[ERROR] No existe $ADB"; exit 115; }

          # Headless, sin snapshot/cámaras para CI
          nohup "$EMU" -avd "$AVD_NAME" -no-window -no-snapshot -no-boot-anim -gpu swiftshader_indirect \
                -camera-back none -camera-front none > emulator.log 2>&1 &

          # Esperar a que aparezca emulator-*
          for i in $(seq 1 90); do
            "$ADB" devices | grep -E "emulator-[0-9]+" && break || true
            sleep 2
          done
          DEV=$("$ADB" devices | awk '/emulator-/{print $1; exit}')
          [ -n "$DEV" ] || { echo "[ERROR] No apareció emulator-*"; exit 116; }

          # Esperar boot completo
          for i in $(seq 1 150); do
            "$ADB" -s "$DEV" shell getprop sys.boot_completed 2>/dev/null | grep -q 1 && break || true
            sleep 2
          done

          # Desbloqueo + carpeta tmp
          "$ADB" -s "$DEV" shell input keyevent 224 || true
          "$ADB" -s "$DEV" shell input keyevent 82  || true
          "$ADB" -s "$DEV" shell input keyevent 3   || true
          "$ADB" -s "$DEV" shell "mkdir -p /data/local/tmp && chmod 777 /data/local/tmp"
        '''
      }
    }

    stage('Ejecutar pruebas (Behave)') {
      steps {
        sh '''
          set -euxo pipefail
          . .venv/bin/activate
          TAGS_TRIM="${BEHAVE_TAGS//\"/}"
          if [ -n "$TAGS_TRIM" ]; then
            python -m behave -t "$TAGS_TRIM" -f allure_behave.formatter:AllureFormatter -o "$REPORTS/allure-results"
          else
            python -m behave -f allure_behave.formatter:AllureFormatter -o "$REPORTS/allure-results"
          fi
        '''
      }
    }
  }

  post {
    always {
      sh '''
        set +e
        ADB="$ANDROID_SDK_ROOT/platform-tools/adb"
        if [ -x "$ADB" ]; then
          DEV=$("$ADB" devices | awk '/emulator-/{print $1; exit}')
          if [ -n "$DEV" ]; then
            "$ADB" -s "$DEV" shell screencap -p /sdcard/final.png || true
            mkdir -p "$REPORTS"
            "$ADB" -s "$DEV" pull /sdcard/final.png "$REPORTS/final.png" >/dev/null 2>&1 || true
            "$ADB" -s "$DEV" emu kill || true
          fi
        fi
        # Cerrar appium
        pkill -f "node .*appium" || pkill -f appium || true
        set -e
      '''
      archiveArtifacts artifacts: 'reports/**', fingerprint: true, onlyIfSuccessful: false, allowEmptyArchive: true
    }
  }
}
