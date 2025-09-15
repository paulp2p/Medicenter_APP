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
    if config.get("PLATFORM_VERSION") or os.getenv("PLATFORM_VERSION"):
        options.set_capability("appium:platformVersion", config.get("PLATFORM_VERSION", os.getenv("PLATFORM_VERSION")))

    # Calidad de vida en CI
    options.set_capability("appium:autoGrantPermissions", True)
    options.set_capability("appium:disableWindowAnimation", True)
    options.set_capability("appium:skipDeviceInitialization", True)
    options.set_capability("appium:newCommandTimeout", int(config.get("NEW_COMMAND_TIMEOUT", 180)))

    # Timeouts amplios para CI (sin duplicación)
    options.set_capability("appium:adbExecTimeout", int(os.getenv("ADB_EXEC_TIMEOUT", "300000")))
    options.set_capability("appium:uiautomator2ServerInstallTimeout", int(os.getenv("UIA2_INSTALL_TIMEOUT", "300000")))
    options.set_capability("appium:uiautomator2ServerLaunchTimeout", int(os.getenv("UIA2_LAUNCH_TIMEOUT", "300000")))
    options.set_capability("appium:androidInstallTimeout", int(os.getenv("ANDROID_INSTALL_TIMEOUT", "300000")))
    options.set_capability("appium:appWaitActivity", config.get("APP_WAIT_ACTIVITY", "*"))

    # Idioma/locale
    options.set_capability("appium:language", os.getenv("LANGUAGE", config.get("LANGUAGE", "en")))
    options.set_capability("appium:locale", os.getenv("LOCALE", config.get("LOCALE", "US")))

    # Útiles para debug y compatibilidad
    options.set_capability("appium:printPageSourceOnFindFailure", True)
    options.set_capability("appium:ignoreHiddenApiPolicyError", True)

    # UDID (si se exporta, lo usamos)
    udid_env = os.getenv("UDID") or config.get("UDID")
    if udid_env:
        options.set_capability("appium:udid", udid_env)

    # Ruta APP (capability 'app') o package/activity
    app_path = os.getenv("APP", config.get("APP"))
    pkg_env = os.getenv("APP_PACKAGE", config.get("APP_PACKAGE"))
    act_env = os.getenv("APP_ACTIVITY", config.get("APP_ACTIVITY"))

    if app_path:
        # --- Normalizar path Windows->Linux (cuando corre en GitHub Actions) ---
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
        # ----------------------------------------------------------------------

        if not os.path.isabs(app_path):
            app_path = os.path.abspath(app_path)
        if not os.path.exists(app_path):
            print(f"[WARN] APP path no existe: {app_path}")
        options.set_capability("appium:app", app_path)

        # BYPASS aapt2: si conocemos package/activity, los seteamos también
        if pkg_env and act_env:
            options.set_capability("appium:appPackage", pkg_env)
            options.set_capability("appium:appActivity", act_env)
            options.set_capability("appium:appWaitActivity", os.getenv("APP_WAIT_ACTIVITY", "*"))
    else:
        if pkg_env:
            options.set_capability("appium:appPackage", pkg_env)
        if act_env:
            options.set_capability("appium:appActivity", act_env)

    # (Opcional) Port dedicado si querés paralelismo futuro
    if os.getenv("SYSTEM_PORT"):
        options.set_capability("appium:systemPort", int(os.getenv("SYSTEM_PORT")))

    pkg_for_log = pkg_env or "<no-package>"
    act_for_log = act_env or ""
    print(f"[driver_factory] Appium server: {server_url}")
    print(f"[driver_factory] Using app: {app_path or (pkg_for_log + '/' + act_for_log)}")

    driver = webdriver.Remote(server_url, options=options)

    # Ajustes de sesión que reducen esperas internas del framework
    try:
        driver.update_settings({
            "waitForIdleTimeout": 0,
            "actionAcknowledgmentTimeout": 0
        })
    except Exception as e:
        print(f"[driver_factory] update_settings warning: {e}")

    return driver
