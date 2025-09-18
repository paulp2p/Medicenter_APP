import os
from appium import webdriver

# Compatibilidad con Appium Python client v3/v2
try:
    from appium.options.android import UiAutomator2Options  # v3+
except Exception:
    from appium.options.android.uiautomator2 import UiAutomator2Options  # v2.x


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

    # Usar el emulador detectado por el workflow (ANDROID_SERIAL/UDID)
    udid = config.get("UDID", os.getenv("UDID"))
    if udid:
        options.set_capability("appium:udid", udid)
        options.set_capability("appium:deviceName", udid)
    else:
        options.set_capability("appium:deviceName", config.get("DEVICE_NAME", os.getenv("DEVICE_NAME", "Android Emulator")))

    if config.get("PLATFORM_VERSION") or os.getenv("PLATFORM_VERSION"):
        options.set_capability("appium:platformVersion", config.get("PLATFORM_VERSION", os.getenv("PLATFORM_VERSION")))

    # Calidad de vida en CI
    options.set_capability("appium:autoGrantPermissions", True)
    options.set_capability("appium:disableWindowAnimation", True)
    options.set_capability("appium:newCommandTimeout", int(config.get("NEW_COMMAND_TIMEOUT", 180)))
    options.set_capability("appium:skipDeviceInitialization", True)

    # Timeouts amplios para CI (emulador TCG es lento)
    options.set_capability("appium:adbExecTimeout", int(os.getenv("ADB_EXEC_TIMEOUT", "600000")))
    options.set_capability("appium:uiautomator2ServerInstallTimeout", int(os.getenv("UIA2_INSTALL_TIMEOUT", "300000")))
    options.set_capability("appium:uiautomator2ServerLaunchTimeout", int(os.getenv("UIA2_LAUNCH_TIMEOUT", "300000")))
    options.set_capability("appium:androidInstallTimeout", int(os.getenv("ANDROID_INSTALL_TIMEOUT", "600000")))

    # Indicamos a Appium que tolere un launch más largo y que realmente lance la app
    options.set_capability("appium:appWaitForLaunch", True)
    options.set_capability("appium:appWaitDuration", int(os.getenv("APP_WAIT_DURATION", "120000")))
    options.set_capability("appium:appWaitActivity", os.getenv("APP_WAIT_ACTIVITY", config.get("APP_WAIT_ACTIVITY", "*")))
    options.set_capability("appium:dontStopAppOnReset", False)

    # Idioma/locale (si tus tests dependen de esto, cámbialo)
    options.set_capability("appium:language", os.getenv("LANGUAGE", config.get("LANGUAGE", "en")))
    options.set_capability("appium:locale", os.getenv("LOCALE", config.get("LOCALE", "US")))

    # Útiles para debug y compatibilidad
    options.set_capability("appium:printPageSourceOnFindFailure", True)
    options.set_capability("appium:ignoreHiddenApiPolicyError", True)

    # Ruta APP (capability 'app') o package/activity
    app_path = os.getenv("APP", config.get("APP"))
    pkg_env = os.getenv("APP_PACKAGE", config.get("APP_PACKAGE"))
    act_env = os.getenv("APP_ACTIVITY", config.get("APP_ACTIVITY"))

    if app_path:
        # Normalizar path Windows->Linux en CI
        if os.name != "nt" and (":\\" in app_path or ":/" in app_path):
            win_basename = os.path.basename(app_path.replace("\\", "/"))
            candidate = os.path.abspath(win_basename)
            if os.path.exists(candidate):
                print(f"[driver_factory] Normalizado APP desde Windows a: {candidate}")
                app_path = candidate
            else:
                gw = os.getenv("GITHUB_WORKSPACE")
                if gw:
                    candidate2 = os.path.join(gw, win_basename)
                    if os.path.exists(candidate2):
                        print(f"[driver_factory] Normalizado APP (workspace) a: {candidate2}")
                        app_path = candidate2

        if not os.path.isabs(app_path):
            app_path = os.path.abspath(app_path)
        if not os.path.exists(app_path):
            print(f"[WARN] APP path no existe: {app_path}")
        options.set_capability("appium:app", app_path)

        # BYPASS del parseo del manifest (evita aapt2)
        if pkg_env and act_env:
            options.set_capability("appium:appPackage", pkg_env)
            options.set_capability("appium:appActivity", act_env)
    else:
        if pkg_env:
            options.set_capability("appium:appPackage", pkg_env)
        if act_env:
            options.set_capability("appium:appActivity", act_env)

    if os.getenv("SYSTEM_PORT"):
        options.set_capability("appium:systemPort", int(os.getenv("SYSTEM_PORT")))

    pkg_for_log = pkg_env or "<no-package>"
    act_for_log = act_env or ""
    print(f"[driver_factory] Appium server: {server_url}")
    print(f"[driver_factory] Using app: {app_path or (pkg_for_log + '/' + act_for_log)}")
    if udid:
        print(f"[driver_factory] UDID/serial: {udid}")

    driver = webdriver.Remote(server_url, options=options)

    # En emulador lento, no conviene poner 0: dejamos 1000ms para que el árbol sea estable
    try:
        driver.update_settings({
            "waitForIdleTimeout": 1000,             # antes lo teníamos en 0
            "actionAcknowledgmentTimeout": 500
        })
    except Exception as e:
        print(f"[driver_factory] update_settings warning: {e}")

    return driver
