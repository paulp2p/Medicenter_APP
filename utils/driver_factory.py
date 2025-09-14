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
    # Opcional: versión del emulador
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

    # UDID si conectás un device físico / o emulador específico
    udid = os.getenv("UDID") or config.get("UDID")
    if udid:
        options.set_capability("appium:udid", udid)


    # === Ruta APP (capability 'app') o package/activity ===
    app_path = os.getenv("APP", config.get("APP"))

    def _normalize_app_path(p: str) -> str:
        """Normaliza rutas que puedan venir estilo Windows y vuelve absoluta en Linux/macOS."""
        if not p:
            return p
        # Reemplazar barras invertidas y quitar prefijo de unidad tipo 'C:'
        p2 = p.replace("\\", "/")
        if len(p2) >= 2 and p2[1] == ":":
            p2 = p2[2:]  # quita 'C:' y deja '/...' o '...'
        # Si no es absoluta, volverla absoluta respecto al workspace (o cwd)
        if not os.path.isabs(p2):
            ws = os.getenv("GITHUB_WORKSPACE", os.getcwd())
            p2 = os.path.join(ws, p2)
        return os.path.normpath(p2)

    resolved_app = None
    if app_path:
        candidate = _normalize_app_path(app_path)
        if os.path.exists(candidate):
            resolved_app = candidate
        else:
            # Fallback fuerte: usar el APK descargado por el workflow
            ws = os.getenv("GITHUB_WORKSPACE", os.getcwd())
            apk_name = os.getenv("APK_LOCAL_NAME", "medicenter_app.apk")
            fallback = os.path.join(ws, apk_name)
            if os.path.exists(fallback):
                print(f"[driver_factory] WARNING: APP no existe ({candidate}). Usando fallback: {fallback}")
                resolved_app = fallback
            else:
                print(f"[WARN] APP path no existe: {candidate} (tampoco fallback: {fallback})")

    if resolved_app:
        options.set_capability("appium:app", resolved_app)
    else:
        # Sin 'app' válida → usar package/activity (requiere que la app esté instalada en el dispositivo)
        options.set_capability("appium:appPackage", os.getenv("APP_PACKAGE", config.get("APP_PACKAGE")))
        options.set_capability("appium:appActivity", os.getenv("APP_ACTIVITY", config.get("APP_ACTIVITY")))

    # (Opcional) Port dedicado si querés paralelismo futuro
    if os.getenv("SYSTEM_PORT"):
        options.set_capability("appium:systemPort", int(os.getenv("SYSTEM_PORT")))

    pkg_for_log = os.getenv("APP_PACKAGE") or config.get("APP_PACKAGE", "<no-package>")
    act_for_log = os.getenv("APP_ACTIVITY") or config.get("APP_ACTIVITY", "")
    print(f"[driver_factory] Appium server: {server_url}")
    print(f"[driver_factory] Using app: {resolved_app or (pkg_for_log + '/' + act_for_log)}")

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
