import os
from appium import webdriver

# Compatibilidad con Appium Python client v3/v2
try:
    # v3+
    from appium.options.android import UiAutomator2Options
except Exception:
    # v2.x
    from appium.options.android.uiautomator2 import UiAutomator2Options


def _bool(val, default=False):
    if val is None:
        return default
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ("1", "true", "yes", "y", "on")


def create_driver(config: dict):
    # URL del servidor Appium (permite override por ENV)
    server_url = config.get("APPIUM_SERVER_URL", os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723"))

    options = UiAutomator2Options()

    # Básico
    options.set_capability("platformName", config.get("PLATFORM_NAME", "Android"))
    options.set_capability("appium:automationName", config.get("AUTOMATION_NAME", "UiAutomator2"))
    options.set_capability("appium:deviceName", config.get("DEVICE_NAME", os.getenv("DEVICE_NAME", "Android Emulator")))
    # Opcional: si querés fijar versión del emulador (no obligatorio)
    if config.get("PLATFORM_VERSION") or os.getenv("PLATFORM_VERSION"):
        options.set_capability("appium:platformVersion", config.get("PLATFORM_VERSION", os.getenv("PLATFORM_VERSION")))

    # Calidad de vida en CI
    options.set_capability("appium:autoGrantPermissions", True)
    options.set_capability("appium:disableWindowAnimation", True)
    options.set_capability("appium:newCommandTimeout", int(config.get("NEW_COMMAND_TIMEOUT", 180)))

    # Reinstalación/estado de app entre runs
    options.set_capability("appium:noReset", _bool(config.get("NO_RESET", os.getenv("NO_RESET", "false"))))
    options.set_capability("appium:fullReset", _bool(config.get("FULL_RESET", os.getenv("FULL_RESET", "false"))))
    # Fuerza reinstalación si la app ya estaba (evita “stale build”)
    options.set_capability("appium:enforceAppInstall", _bool(os.getenv("ENFORCE_APP_INSTALL", "true"), True))

    # Esperas largas (Windows/emulador sin aceleración pueden tardar)
    options.set_capability("appium:adbExecTimeout", int(os.getenv("ADB_EXEC_TIMEOUT", "240000")))
    options.set_capability("appium:uiautomator2ServerInstallTimeout", int(os.getenv("UIA2_INSTALL_TIMEOUT", "240000")))
    options.set_capability("appium:uiautomator2ServerLaunchTimeout", int(os.getenv("UIA2_LAUNCH_TIMEOUT", "240000")))
    options.set_capability("appium:appWaitActivity", config.get("APP_WAIT_ACTIVITY", "*"))

    # Idioma/locale (el workflow setea LANGUAGE=en, LOCALE=US)
    options.set_capability("appium:language", os.getenv("LANGUAGE", config.get("LANGUAGE", "en")))
    options.set_capability("appium:locale", os.getenv("LOCALE", config.get("LOCALE", "US")))

    # Útiles para debug y compatibilidad
    options.set_capability("appium:printPageSourceOnFindFailure", True)
    options.set_capability("appium:ignoreHiddenApiPolicyError", True)

    # UDID si conectás un device físico
    if config.get("UDID"):
        options.set_capability("appium:udid", config["UDID"])

    # Ruta APP (capability 'app') o package/activity
    app_path = os.getenv("APP", config.get("APP"))
    if app_path:
        # Normaliza ruta relativa/absoluta (soporta Windows y Linux)
        if not os.path.isabs(app_path):
            app_path = os.path.abspath(app_path)
        if not os.path.exists(app_path):
            print(f"[WARN] APP path no existe: {app_path}")
        options.set_capability("appium:app", app_path)
    else:
        options.set_capability("appium:appPackage", os.getenv("APP_PACKAGE", config.get("APP_PACKAGE")))
        options.set_capability("appium:appActivity", os.getenv("APP_ACTIVITY", config.get("APP_ACTIVITY")))

    # (Opcional) Port dedicado si querés paralelismo futuro
    if os.getenv("SYSTEM_PORT"):
        options.set_capability("appium:systemPort", int(os.getenv("SYSTEM_PORT")))

    print(f"[driver_factory] Appium server: {server_url}")
    print(f"[driver_factory] Using app: {app_path or (os.getenv('APP_PACKAGE') + '/' + os.getenv('APP_ACTIVITY', ''))}")

    driver = webdriver.Remote(server_url, options=options)

    # Ajustes de sesión que reducen esperas internas del framework
    try:
        driver.update_settings({
            # Evita esperas por “idle” del UI Automator si tu app es dinámica
            "waitForIdleTimeout": 0,
            "actionAcknowledgmentTimeout": 0
        })
    except Exception as e:
        print(f"[driver_factory] update_settings warning: {e}")

    return driver
