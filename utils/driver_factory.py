# driver_factory.py
import os
from appium import webdriver

# Compat: Appium Python client v2
try:
    from appium.options.android.uiautomator2 import UiAutomator2Options
except Exception:
    # fallback por si hay una versión anterior del cliente
    from appium.options.android import UiAutomator2Options


def _to_bool(val, default=False):
    if val is None:
        return default
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ("1", "true", "yes", "on")


def _int(env_name: str, default: int) -> int:
    try:
        return int(os.getenv(env_name, "").strip() or default)
    except Exception:
        return default


def create_driver(config: dict):
    """
    Crea el driver de Appium para UiAutomator2 con settings robustos para CI.
    - Evita `pm clear` (noReset=True por defecto) → elimina el timeout de Package Manager.
    - Timeouts amplios para ADB y UIA2 server.
    - Fuerza idioma en-US (language/locale).
    - Si APP_PATH está presente, se asume APK ya instalada vía ADB y NO se envía 'app'.
    """

    server_url = os.getenv("APPIUM_SERVER_URL") or config.get(
        "APPIUM_SERVER_URL", "http://127.0.0.1:4723"
    )

    # Timeouts/idioma con override por env
    adb_exec_timeout_ms = _int("ADB_EXEC_TIMEOUT_MS", 120_000)  # 120s
    uia2_install_timeout_ms = _int("UIA2_INSTALL_TIMEOUT_MS", 120_000)
    uia2_launch_timeout_ms = _int("UIA2_LAUNCH_TIMEOUT_MS", 120_000)
    app_wait_duration_ms = _int("APP_WAIT_DURATION_MS", 120_000)
    new_command_timeout_s = _int("NEW_COMMAND_TIMEOUT_S", int(config.get("NEW_COMMAND_TIMEOUT", 120)))

    lang = os.getenv("APPIUM_LANGUAGE", "en")
    loc = os.getenv("APPIUM_LOCALE", "US")

    options = UiAutomator2Options()

    # W3C caps principales
    options.set_capability("platformName", config.get("PLATFORM_NAME", "Android"))
    options.set_capability("appium:automationName", config.get("AUTOMATION_NAME", "UiAutomator2"))
    options.set_capability("appium:deviceName", config.get("DEVICE_NAME", os.getenv("DEVICE_NAME", "Android Emulator")))
    options.set_capability("appium:newCommandTimeout", new_command_timeout_s)
    options.set_capability("appium:disableWindowAnimation", True)
    options.set_capability("appium:autoGrantPermissions", True)

    # Robustez CI / performance
    options.set_capability("appium:ignoreHiddenApiPolicyError", True)
    options.set_capability("appium:skipDeviceInitialization", True)
    options.set_capability("appium:androidInstallTimeout", _int("ANDROID_INSTALL_TIMEOUT_MS", 300_000))  # 5 min
    options.set_capability("appium:enforceAppInstall", False)
    options.set_capability("appium:appWaitActivity", config.get("APP_WAIT_ACTIVITY", "*"))
    options.set_capability("appium:appWaitForLaunch", False)   # no esperar launch blocking
    options.set_capability("appium:dontStopAppOnReset", True)
    options.set_capability("appium:autoLaunch", False)         # no lanzar app en NEW_SESSION

    # 🔴 Clave para evitar `pm clear`: noReset=True (override por env/CONFIG si querés)
    # Si querés forzar reset, seteá NO_RESET=0 y/o FULL_RESET=1 explícitamente.
    options.set_capability("appium:noReset", _to_bool(os.getenv("APPIUM_NO_RESET"), True)
                           if os.getenv("APPIUM_NO_RESET") is not None
                           else _to_bool(config.get("NO_RESET", "True"), True))
    options.set_capability("appium:fullReset", _to_bool(config.get("FULL_RESET", "False"), False))

    # Timeouts extra para evitar flakiness de ADB/UiAutomator2
    options.set_capability("appium:adbExecTimeout", adb_exec_timeout_ms)
    options.set_capability("appium:uiautomator2ServerInstallTimeout", uia2_install_timeout_ms)
    options.set_capability("appium:uiautomator2ServerLaunchTimeout", uia2_launch_timeout_ms)
    options.set_capability("appium:appWaitDuration", app_wait_duration_ms)

    # Idioma por caps (refuerzo al ADB 'cmd locale set' del workflow)
    options.set_capability("appium:language", lang)
    options.set_capability("appium:locale", loc)

    # UDID opcional (útil si tenés más de un emu/dispositivo)
    udid = config.get("UDID") or os.getenv("UDID")
    if udid:
        options.set_capability("appium:udid", udid)

    # Package/Activity obligatorios si no vas a pasar 'app'
    app_package = config.get("APP_PACKAGE") or os.getenv("APP_PACKAGE")
    if not app_package:
        raise RuntimeError("[driver_factory] Falta APP_PACKAGE.")
    options.set_capability("appium:appPackage", app_package)

    app_activity = config.get("APP_ACTIVITY") or os.getenv("APP_ACTIVITY")
    if app_activity:
        options.set_capability("appium:appActivity", app_activity)

    # Estrategia CI:
    # - Si APP_PATH está en env, asumimos que la APK YA fue instalada por ADB en el workflow → NO enviar 'app'.
    # - Si no, permitimos instalar desde ruta local (CONFIG.APP).
    if os.getenv("APP_PATH"):
        print(f"[driver_factory] CI con APK preinstalada: omito 'app' y usaré package/activity: "
              f"{app_package}/{app_activity or '*'}")
    else:
        app_local = config.get("APP")
        if app_local:
            if not os.path.exists(app_local):
                raise FileNotFoundError(f"[driver_factory] APP apunta a un archivo inexistente: {app_local}")
            options.set_capability("appium:app", app_local)
            print(f"[driver_factory] Instalando APK local (APP): {app_local}")
        else:
            print(f"[driver_factory] Launch por package/activity: {app_package}/{app_activity or '*'} (sin 'app')")

    # Log rápido de caps sensibles para debug (sin exponer secretos)
    print("[driver_factory] Caps clave -> noReset="
          f"{options.capabilities.get('appium:noReset')} | "
          f"adbExecTimeout={options.capabilities.get('appium:adbExecTimeout')}ms | "
          f"lang={lang}-{loc}")

    return webdriver.Remote(server_url, options=options)
