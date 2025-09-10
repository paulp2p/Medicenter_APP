import os
from appium import webdriver
try:
    # Appium Python <=2
    from appium.options.android.uiautomator2 import UiAutomator2Options
except Exception:
    # Appium Python >=3
    from appium.options.android import UiAutomator2Options

def create_driver(config):
    server_url = config.get("APPIUM_SERVER_URL", os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723"))

    options = UiAutomator2Options()
    options.set_capability("platformName", config.get("PLATFORM_NAME", "Android"))
    options.set_capability("appium:automationName", config.get("AUTOMATION_NAME", "UiAutomator2"))
    options.set_capability("appium:deviceName", config.get("DEVICE_NAME", os.getenv("DEVICE_NAME", "Android Emulator")))

    # Calidad de vida en CI
    options.set_capability("appium:autoGrantPermissions", True)
    options.set_capability("appium:newCommandTimeout", int(config.get("NEW_COMMAND_TIMEOUT", 120)))
    options.set_capability("appium:noReset", str(config.get("NO_RESET", "False")).lower() == "true")
    options.set_capability("appium:fullReset", str(config.get("FULL_RESET", "False")).lower() == "true")
    options.set_capability("appium:disableWindowAnimation", True)
    options.set_capability("appium:appWaitActivity", config.get("APP_WAIT_ACTIVITY", "*"))
    options.set_capability("appium:adbExecTimeout", 120000)
    options.set_capability("appium:uiautomator2ServerInstallTimeout", 120000)

    # Idioma/locale (el workflow usa en-US)
    lang = os.getenv("LANGUAGE", config.get("LANGUAGE", "en"))
    loc  = os.getenv("LOCALE",   config.get("LOCALE", "US"))
    options.set_capability("appium:language", lang)
    options.set_capability("appium:locale",   loc)

    if config.get("UDID"):
        options.set_capability("appium:udid", config["UDID"])

    # APP por env o config (capability 'app'); si no, package/activity
    app_path = os.getenv("APP", config.get("APP"))
    if app_path:
        if not os.path.isabs(app_path):
            # Por si te pasan relativo
            app_path = os.path.abspath(app_path)
        if not os.path.exists(app_path):
            print(f"[WARN] APP path no existe: {app_path}")
        options.set_capability("appium:app", app_path)
    else:
        options.set_capability("appium:appPackage", os.getenv("APP_PACKAGE", config.get("APP_PACKAGE")))
        options.set_capability("appium:appActivity", os.getenv("APP_ACTIVITY", config.get("APP_ACTIVITY")))

    return webdriver.Remote(server_url, options=options)
