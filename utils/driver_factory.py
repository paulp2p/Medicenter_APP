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
    server_url = os.getenv("APPIUM_SERVER_URL") or config.get("APPIUM_SERVER_URL", "http://127.0.0.1:4723")

    options = UiAutomator2Options()
    options.set_capability("platformName",                  config.get("PLATFORM_NAME", "Android"))
    options.set_capability("appium:automationName",         config.get("AUTOMATION_NAME", "UiAutomator2"))
    options.set_capability("appium:deviceName",             config.get("DEVICE_NAME", os.getenv("DEVICE_NAME", "Android Emulator")))
    options.set_capability("appium:autoGrantPermissions",   True)
    options.set_capability("appium:newCommandTimeout",      int(config.get("NEW_COMMAND_TIMEOUT", 120)))
    options.set_capability("appium:noReset",                _to_bool(config.get("NO_RESET",  "False")))
    options.set_capability("appium:fullReset",              _to_bool(config.get("FULL_RESET","False")))
    options.set_capability("appium:disableWindowAnimation", True)

    # Robustez/velocidad en CI
    options.set_capability("appium:ignoreHiddenApiPolicyError", True)
    options.set_capability("appium:skipDeviceInitialization",   True)
    options.set_capability("appium:androidInstallTimeout",      int(os.getenv("ANDROID_INSTALL_TIMEOUT_MS", "300000")))  # 5 min
    options.set_capability("appium:enforceAppInstall",          False)
    options.set_capability("appium:appWaitActivity",            config.get("APP_WAIT_ACTIVITY", "*"))
    options.set_capability("appium:appWaitForLaunch",           False)
    options.set_capability("appium:dontStopAppOnReset",         True)
    options.set_capability("appium:autoLaunch",                 False)  # no lanzar en NEW_SESSION

    udid = config.get("UDID") or os.getenv("UDID")
    if udid:
        options.set_capability("appium:udid", udid)

    app_package  = config.get("APP_PACKAGE")  or os.getenv("APP_PACKAGE")
    if not app_package:
        raise RuntimeError("[driver_factory] Falta APP_PACKAGE.")
    options.set_capability("appium:appPackage", app_package)

    app_activity = config.get("APP_ACTIVITY") or os.getenv("APP_ACTIVITY")
    if app_activity:
        options.set_capability("appium:appActivity", app_activity)

    # CI: si APP_PATH está presente, NO pasamos 'app' (ya instalamos por adb)
    if os.getenv("APP_PATH"):
        print(f"[driver_factory] CI con APK preinstalada: omito 'app' y usaré package/activity: {app_package}/{app_activity or '*'}")
    else:
        app_local = config.get("APP")
        if app_local:
            if not os.path.exists(app_local):
                raise FileNotFoundError(f"[driver_factory] APP apunta a un archivo inexistente: {app_local}")
            options.set_capability("appium:app", app_local)
            print(f"[driver_factory] Instalando APK local (APP): {app_local}")
        else:
            print(f"[driver_factory] Launch por package/activity: {app_package}/{app_activity or '*'} (sin 'app')")

    return webdriver.Remote(server_url, options=options)
