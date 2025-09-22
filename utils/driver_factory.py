import os
from appium import webdriver

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
    server_url = config.get("APPIUM_SERVER_URL", os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723"))
    options = UiAutomator2Options()

    # Básico
    options.set_capability("platformName", config.get("PLATFORM_NAME", "Android"))
    options.set_capability("appium:automationName", config.get("AUTOMATION_NAME", "UiAutomator2"))

    # Dirigimos al emulador detectado por el workflow
    udid = config.get("UDID", os.getenv("UDID"))
    if udid:
        options.set_capability("appium:udid", udid)
        options.set_capability("appium:deviceName", udid)
    else:
        options.set_capability("appium:deviceName", config.get("DEVICE_NAME", os.getenv("DEVICE_NAME", "Android Emulator")))

    if config.get("PLATFORM_VERSION") or os.getenv("PLATFORM_VERSION"):
        options.set_capability("appium:platformVersion", config.get("PLATFORM_VERSION", os.getenv("PLATFORM_VERSION")))

    # Perfil según KVM (HAS_KVM=1 lo setea el workflow si /dev/kvm está ok)
    HAS_KVM = _bool(os.getenv("HAS_KVM"), False)

    # Timeouts base (más cortos con KVM)
    adb_exec_timeout_ms = 180_000 if HAS_KVM else int(os.getenv("ADB_EXEC_TIMEOUT", "600000"))
    uia2_install_timeout_ms = 120_000 if HAS_KVM else int(os.getenv("UIA2_INSTALL_TIMEOUT", "300000"))
    uia2_launch_timeout_ms  = 120_000 if HAS_KVM else int(os.getenv("UIA2_LAUNCH_TIMEOUT", "300000"))
    android_install_timeout = 240_000 if HAS_KVM else int(os.getenv("ANDROID_INSTALL_TIMEOUT", "600000"))
    app_wait_duration_ms    = 60_000  if HAS_KVM else int(os.getenv("APP_WAIT_DURATION", "120000"))

    # Calidad de vida en CI
    options.set_capability("appium:autoGrantPermissions", True)
    options.set_capability("appium:disableWindowAnimation", True)
    options.set_capability("appium:newCommandTimeout", int(config.get("NEW_COMMAND_TIMEOUT", 180)))
    options.set_capability("appium:skipDeviceInitialization", True)
    options.set_capability("appium:disableAndroidWatchers", True)  # reduce overhead de watchers

    # Timeouts
    options.set_capability("appium:adbExecTimeout", adb_exec_timeout_ms)
    options.set_capability("appium:uiautomator2ServerInstallTimeout", uia2_install_timeout_ms)
    options.set_capability("appium:uiautomator2ServerLaunchTimeout", uia2_launch_timeout_ms)
    options.set_capability("appium:androidInstallTimeout", android_install_timeout)

    # Launch/wait de la app
    options.set_capability("appium:appWaitForLaunch", True)
    options.set_capability("appium:appWaitDuration", app_wait_duration_ms)

    # appWaitActivity más específico si está APP_ACTIVITY; sino, fallback regex
    pkg_env = os.getenv("APP_PACKAGE", config.get("APP_PACKAGE"))
    act_env = os.getenv("APP_ACTIVITY", config.get("APP_ACTIVITY"))
    if act_env:
        # Regex permite pequeñas variaciones (por ejemplo .MainActivity vs .MainActivityAlias)
        options.set_capability("appium:appWaitActivity", f"{act_env}.*")
    else:
        options.set_capability("appium:appWaitActivity", os.getenv("APP_WAIT_ACTIVITY", config.get("APP_WAIT_ACTIVITY", ".*")))

    options.set_capability("appium:dontStopAppOnReset", False)

    # Idioma/locale (ajústalo si tus tests dependen de ES/AR)
    options.set_capability("appium:language", os.getenv("LANGUAGE", config.get("LANGUAGE", "en")))
    options.set_capability("appium:locale", os.getenv("LOCALE", config.get("LOCALE", "US")))

    # Útiles para debug y compatibilidad
    options.set_capability("appium:printPageSourceOnFindFailure", True)
    options.set_capability("appium:ignoreHiddenApiPolicyError", True)

    # Ruta APP (o package/activity)
    app_path = os.getenv("APP", config.get("APP"))
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

        # BYPASS manifest si ya pasamos pkg/activity por env
        if pkg_env and act_env:
            options.set_capability("appium:appPackage", pkg_env)
            options.set_capability("appium:appActivity", act_env)
    else:
        if pkg_env:
            options.set_capability("appium:appPackage", pkg_env)
        if act_env:
            options.set_capability("appium:appActivity", act_env)

    # System port (paralelismo)
    if os.getenv("SYSTEM_PORT"):
        options.set_capability("appium:systemPort", int(os.getenv("SYSTEM_PORT")))

    print(f"[driver_factory] Appium server: {server_url}")
    print(f"[driver_factory] Using app: {app_path or (pkg_env or '<no-package>') + '/' + (act_env or '')}")
    if udid:
        print(f"[driver_factory] UDID/serial: {udid}")
    print(f"[driver_factory] HAS_KVM={HAS_KVM}")

    driver = webdriver.Remote(server_url, options=options)

    # UIA2 settings: estabilidad del árbol (1s) y ack rápido
    try:
        driver.update_settings({
            "waitForIdleTimeout": 1000,
            "actionAcknowledgmentTimeout": 500
        })
    except Exception as e:
        print(f"[driver_factory] update_settings warning: {e}")

    return driver
