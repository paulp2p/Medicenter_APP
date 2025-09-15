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

    # Calidad de vida / CI
    options.set_capability("appium:autoGrantPermissions", True)
    options.set_capability("appium:disableWindowAnimation", True)
    options.set_capability("appium:skipDeviceInitialization", True)
    options.set_capability("appium:newCommandTimeout", int(config.get("NEW_COMMAND_TIMEOUT", 180)))

    # Timeouts generosos para CI
    options.set_capability("appium:adbExecTimeout", int(os.getenv("ADB_EXEC_TIMEOUT", "300000")))
    options.set_capability("appium:uiautomator2ServerInstallTimeout", int(os.getenv("UIA2_INSTALL_TIMEOUT", "300000")))
    options.set_capability("appium:uiautomator2ServerLaunchTimeout", int(os.getenv("UIA2_LAUNCH_TIMEOUT", "300000")))
    options.set_capability("appium:androidInstallTimeout", int(os.getenv("ANDROID_INSTALL_TIMEOUT", "300000")))

    # Estado de app entre runs
    options.set_capability("appium:noReset", _bool(config.get("NO_RESET", os.getenv("NO_RESET", "true"))))
    options.set_capability("appium:fullReset", _bool(config.get("FULL_RESET", os.getenv("FULL_RESET", "false"))))
    # *** Muy importante: NO forzar reinstalación desde Appium si ya la instalamos con ADB
    options.set_capability("appium:enforceAppInstall", _bool(os.getenv("ENFORCE_APP_INSTALL", "false")))

    # Espera de actividad inicial
    options.set_capability("appium:appWaitActivity", config.get("APP_WAIT_ACTIVITY", os.getenv("APP_WAIT_ACTIVITY", "*")))

    # Idioma/locale
    options.set_capability("appium:language", os.getenv("LANGUAGE", config.get("LANGUAGE", "en")))
    options.set_capability("appium:locale", os.getenv("LOCALE", config.get("LOCALE", "US")))

    # Útiles para debug y compatibilidad
    options.set_capability("appium:printPageSourceOnFindFailure", True)
    options.set_capability("appium:ignoreHiddenApiPolicyError", True)
    options.set_capability("appium:dontStopAppOnReset", True)

    # UDID si conectás un device físico
    if config.get("UDID"):
        options.set_capability("appium:udid", config["UDID"])

    # Fuentes de configuración
    app_path = os.getenv("APP", config.get("APP"))
    pkg_env = os.getenv("APP_PACKAGE", config.get("APP_PACKAGE"))
    act_env = os.getenv("APP_ACTIVITY", config.get("APP_ACTIVITY"))
    preinstalled = _bool(os.getenv("PREINSTALLED_APP", "true"))

    if preinstalled:
        # NO pasamos 'app' para que Appium NO intente reinstalar
        if pkg_env:
            options.set_capability("appium:appPackage", pkg_env)
        if act_env:
            options.set_capability("appium:appActivity", act_env)
    else:
        # Caso contrario, sí instalamos con Appium
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

            # Bypass aapt2: si tenemos package/activity, setearlos también
            if pkg_env:
                options.set_capability("appium:appPackage", pkg_env)
            if act_env:
                options.set_capability("appium:appActivity", act_env)
        else:
            # Sin 'app', usamos package/activity
            if pkg_env:
                options.set_capability("appium:appPackage", pkg_env)
            if act_env:
                options.set_capability("appium:appActivity", act_env)

    # (Opcional) Port dedicado
    if os.getenv("SYSTEM_PORT"):
        options.set_capability("appium:systemPort", int(os.getenv("SYSTEM_PORT")))

    pkg_for_log = pkg_env or "<no-package>"
    act_for_log = act_env or ""
    using_app = app_path if (not preinstalled and app_path) else (pkg_for_log + '/' + act_for_log)
    print(f"[driver_factory] Appium server: {server_url}")
    print(f"[driver_factory] Using app: {using_app}")

    driver = webdriver.Remote(server_url, options=options)

    # Ajustes de sesión
    try:
        driver.update_settings({
            "waitForIdleTimeout": 0,
            "actionAcknowledgmentTimeout": 0
        })
    except Exception as e:
        print(f"[driver_factory] update_settings warning: {e}")

    return driver
