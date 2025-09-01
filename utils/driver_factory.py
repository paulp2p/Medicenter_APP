# utils/driver_factory.py
import os
from appium import webdriver
from appium.options.android import UiAutomator2Options

def _to_bool(val, default=False):
    if val is None:
        return default
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ("1", "true", "yes", "on")

def create_driver(config):
    # URL de Appium: permite override por env en CI si lo necesitás
    server_url = os.getenv("APPIUM_SERVER_URL") or config.get("APPIUM_SERVER_URL", "http://127.0.0.1:4723")

    options = UiAutomator2Options()
    options.set_capability("platformName",   config.get("PLATFORM_NAME", "Android"))
    options.set_capability("appium:automationName", config.get("AUTOMATION_NAME", "UiAutomator2"))
    options.set_capability("appium:deviceName",     config.get("DEVICE_NAME", os.getenv("DEVICE_NAME", "Android Emulator")))

    options.set_capability("appium:autoGrantPermissions", True)
    options.set_capability("appium:newCommandTimeout", int(config.get("NEW_COMMAND_TIMEOUT", 120)))
    options.set_capability("appium:noReset",  _to_bool(config.get("NO_RESET",  "False")))
    options.set_capability("appium:fullReset", _to_bool(config.get("FULL_RESET","False")))
    options.set_capability("appium:disableWindowAnimation", True)
    options.set_capability("appium:appWaitActivity", config.get("APP_WAIT_ACTIVITY", "*"))

    # ==== FIX CI: evitar init de device + tolerar latencias ADB/UIA2 ====
    options.set_capability("appium:skipDeviceInitialization", True)
    options.set_capability("appium:ignoreHiddenApiPolicyError", True)
    options.set_capability("appium:adbExecTimeout", 120000)                # 120s
    options.set_capability("appium:uiautomator2ServerInstallTimeout", 120000)

    # UDID opcional (emulador/dispositivo físico)
    udid = config.get("UDID") or os.getenv("UDID")
    if udid:
        options.set_capability("appium:udid", udid)

    # ===== Selección de app =====
    # Prioridad: APP_PATH (inyectado por CI) -> APP (si lo usabas antes) -> package/activity
    app_path = (config.get("APP_PATH") or os.getenv("APP_PATH") or config.get("APP"))
    if app_path:
        if os.path.exists(app_path):
            options.set_capability("appium:app", app_path)
            print(f"[driver_factory] Usando APK local (APP_PATH/APP): {app_path}")
        else:
            raise FileNotFoundError(f"[driver_factory] APP_PATH/APP apunta a un archivo inexistente: {app_path}")
    else:
        app_package = config.get("APP_PACKAGE") or os.getenv("APP_PACKAGE")
        app_activity = config.get("APP_ACTIVITY") or os.getenv("APP_ACTIVITY")
        if not app_package or not app_activity:
            raise RuntimeError("[driver_factory] Faltan APP_PACKAGE/APP_ACTIVITY y no hay APP_PATH/APP definido.")
        options.set_capability("appium:appPackage", app_package)
        options.set_capability("appium:appActivity", app_activity)
        print(f"[driver_factory] Launch por package/activity: {app_package}/{app_activity}")

    return webdriver.Remote(server_url, options=options)
