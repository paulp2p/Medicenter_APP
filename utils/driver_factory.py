import os
from appium import webdriver

# Appium Python client v3+ / v2.x
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


def _csv_env(name: str):
    raw = os.getenv(name, "")
    return [x.strip() for x in raw.split(",") if x.strip()]


def create_driver(config: dict):
    # ===== Hub / Server: AHORA ENV -> CONFIG -> DEFAULT =====
    server_url = os.getenv("APPIUM_SERVER_URL", config.get("APPIUM_SERVER_URL", "http://127.0.0.1:4723"))
    is_sauce = "saucelabs.com" in server_url

    options = UiAutomator2Options()

    # ===== Básico =====
    options.set_capability("platformName", os.getenv("PLATFORM_NAME", config.get("PLATFORM_NAME", "Android")))
    options.set_capability("appium:automationName", os.getenv("AUTOMATION_NAME", config.get("AUTOMATION_NAME", "UiAutomator2")))

    # Device / UDID
    udid = os.getenv("UDID", config.get("UDID"))
    if udid:
        options.set_capability("appium:udid", udid)
        options.set_capability("appium:deviceName", udid)
    else:
        options.set_capability("appium:deviceName", os.getenv("DEVICE_NAME", config.get("DEVICE_NAME", "Android Emulator")))

    # platformVersion (ENV primero)
    if os.getenv("PLATFORM_VERSION") or config.get("PLATFORM_VERSION"):
        options.set_capability("appium:platformVersion", os.getenv("PLATFORM_VERSION", config.get("PLATFORM_VERSION")))

    # Perfil KVM vs hosted (sólo para local/hosted)
    HAS_KVM = _bool(os.getenv("HAS_KVM"), False)

    # Timeouts (más cortos con KVM; más largos en hosted)
    adb_exec_timeout_ms     = 180_000 if HAS_KVM else int(os.getenv("ADB_EXEC_TIMEOUT", "600000"))
    uia2_install_timeout_ms = 120_000 if HAS_KVM else int(os.getenv("UIA2_INSTALL_TIMEOUT", "300000"))
    uia2_launch_timeout_ms  = 120_000 if HAS_KVM else int(os.getenv("UIA2_LAUNCH_TIMEOUT", "300000"))
    android_install_timeout = 240_000 if HAS_KVM else int(os.getenv("ANDROID_INSTALL_TIMEOUT", "600000"))
    app_wait_duration_ms    = int(os.getenv("APP_WAIT_DURATION", "60000" if HAS_KVM else "180000"))

    # Calidad de vida en CI
    options.set_capability("appium:autoGrantPermissions", True)
    options.set_capability("appium:disableWindowAnimation", True)
    options.set_capability("appium:newCommandTimeout", int(os.getenv("NEW_COMMAND_TIMEOUT", config.get("NEW_COMMAND_TIMEOUT", 180))))
    options.set_capability("appium:skipDeviceInitialization", True)
    options.set_capability("appium:disableAndroidWatchers", True)

    # Timeouts
    options.set_capability("appium:adbExecTimeout", adb_exec_timeout_ms)
    options.set_capability("appium:uiautomator2ServerInstallTimeout", uia2_install_timeout_ms)
    options.set_capability("appium:uiautomator2ServerLaunchTimeout", uia2_launch_timeout_ms)
    options.set_capability("appium:androidInstallTimeout", android_install_timeout)

    # Launch/wait de la app (relajado para evitar "never started")
    options.set_capability("appium:appWaitForLaunch", False)
    options.set_capability("appium:appWaitDuration", app_wait_duration_ms)

    # appWaitActivity: ENV -> strict -> libre
    pkg_env = os.getenv("APP_PACKAGE", config.get("APP_PACKAGE"))
    act_env = os.getenv("APP_ACTIVITY", config.get("APP_ACTIVITY"))
    strict_wait = _bool(os.getenv("STRICT_APP_WAIT"), False)
    app_wait_activity_env = os.getenv("APP_WAIT_ACTIVITY", config.get("APP_WAIT_ACTIVITY"))
    if app_wait_activity_env:
        options.set_capability("appium:appWaitActivity", app_wait_activity_env)
    elif strict_wait and act_env:
        options.set_capability("appium:appWaitActivity", f"{act_env}.*")
    else:
        options.set_capability("appium:appWaitActivity", ".*")

    # Reset/instalación (Appium NO fuerza reinstalar; lo maneja el workflow)
    options.set_capability("appium:noReset", _bool(os.getenv("NO_RESET", "true"), True))
    options.set_capability("appium:enforceAppInstall", _bool(os.getenv("ENFORCE_APP_INSTALL", "false"), False))
    options.set_capability("appium:dontStopAppOnReset", False)

    # Idioma/locale
    options.set_capability("appium:language", os.getenv("LANGUAGE", config.get("LANGUAGE", "en")))
    options.set_capability("appium:locale", os.getenv("LOCALE", config.get("LOCALE", "US")))

    # Útiles para debug y compatibilidad
    options.set_capability("appium:printPageSourceOnFindFailure", True)
    options.set_capability("appium:ignoreHiddenApiPolicyError", True)

    # ===== APP: ENV primero; soporta IDs/URLs de cloud =====
    app_path = os.getenv("APP") or config.get("APP")
    if app_path:
        # Si es id/url de cloud, no tocamos rutas locales
        if app_path.startswith(("storage:", "sauce-storage:", "bs://")):
            options.set_capability("appium:app", app_path)
        else:
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

        # BYPASS manifest si ya pasamos pkg/activity
        if pkg_env and act_env:
            options.set_capability("appium:appPackage", pkg_env)
            options.set_capability("appium:appActivity", act_env)
    else:
        if pkg_env:
            options.set_capability("appium:appPackage", pkg_env)
        if act_env:
            options.set_capability("appium:appActivity", act_env)

    # System port (paralelismo local)
    if os.getenv("SYSTEM_PORT"):
        options.set_capability("appium:systemPort", int(os.getenv("SYSTEM_PORT")))

    # ===== Sauce Labs: metadata opcional (dashboard) =====
    if is_sauce:
        sauce_opts = {
            "build": os.getenv("SAUCE_BUILD", f"Build #{os.getenv('GITHUB_RUN_NUMBER', 'local')}"),
            "name":  os.getenv("SAUCE_NAME",  "Behave run"),
            "tags":  _csv_env("SAUCE_TAGS") or [os.getenv("GITHUB_REF_NAME", "CI"), "Android", "Behave"],
        }
        if os.getenv("SAUCE_TUNNEL_NAME"):
            sauce_opts["tunnelName"] = os.getenv("SAUCE_TUNNEL_NAME")
        if os.getenv("APPIUM_VERSION"):
            sauce_opts["appiumVersion"] = os.getenv("APPIUM_VERSION")
        if os.getenv("DEVICE_ORIENTATION"):
            sauce_opts["deviceOrientation"] = os.getenv("DEVICE_ORIENTATION")
        options.set_capability("sauce:options", sauce_opts)

    # ===== Logs de arranque =====
    print(f"[driver_factory] Appium server: {server_url}")
    print(f"[driver_factory] Using app: {app_path or (pkg_env or '<no-package>') + '/' + (act_env or '')}")
    if udid:
        print(f"[driver_factory] UDID/serial: {udid}")
    print(f"[driver_factory] HAS_KVM={HAS_KVM}")
    print(f"[driver_factory] appWaitActivity={options.capabilities.get('appium:appWaitActivity')}, "
          f"appWaitDuration={app_wait_duration_ms}ms, noReset={options.capabilities.get('appium:noReset')}")
    if is_sauce:
        print(f"[driver_factory] sauce:options = {options.capabilities.get('sauce:options')}")

    # ===== Crear sesión =====
    driver = webdriver.Remote(server_url, options=options)

    # Ajustes UIA2: árbol más estable
    try:
        driver.update_settings({
            "waitForIdleTimeout": 1000,
            "actionAcknowledgmentTimeout": 500
        })
    except Exception as e:
        print(f"[driver_factory] update_settings warning: {e}")

    return driver
