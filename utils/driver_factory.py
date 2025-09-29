from appium import webdriver
from appium.options.android import UiAutomator2Options

def _bool(v, default=False):
    if v is None:
        return default
    return str(v).strip().lower() in ("1", "true", "yes", "y")

def create_driver(config):
    server_url = config.get("APPIUM_SERVER_URL", "http://127.0.0.1:4723")

    options = UiAutomator2Options()

    # Identidad de plataforma / dispositivo
    options.set_capability("platformName", config.get("PLATFORM_NAME", "Android"))
    options.set_capability("appium:automationName", config.get("AUTOMATION_NAME", "UiAutomator2"))
    options.set_capability("appium:deviceName", config.get("DEVICE_NAME"))

    # ⚠️ RESET por sesión (garantiza "first-run" SIEMPRE)
    # noReset=False -> Appium hace 'pm clear <package>' al iniciar la sesión.
    options.set_capability("appium:noReset", _bool(config.get("NO_RESET", "false"), False))
    options.set_capability("appium:fullReset", _bool(config.get("FULL_RESET", "false"), False))

    # Robustez / velocidad
    options.set_capability("appium:autoGrantPermissions", True)
    options.set_capability("appium:newCommandTimeout", int(config.get("NEW_COMMAND_TIMEOUT", 120)))
    options.set_capability("appium:disableWindowAnimation", True)
    options.set_capability("appium:ignoreUnimportantViews", True)
    options.set_capability("appium:uiautomator2ServerInstallTimeout", int(config.get("UIA2_INSTALL_TIMEOUT", 120000)))
    options.set_capability("appium:uiautomator2ServerLaunchTimeout", int(config.get("UIA2_LAUNCH_TIMEOUT", 120000)))
    options.set_capability("appium:adbExecTimeout", int(config.get("ADB_EXEC_TIMEOUT", 120000)))
    options.set_capability("appium:appWaitActivity", config.get("APP_WAIT_ACTIVITY", "*"))
    options.set_capability("appium:appWaitForLaunch", False)

    # APP vs PACKAGE/ACTIVITY
    if config.get("UDID"):
        options.set_capability("appium:udid", config["UDID"])

    if config.get("APP"):
        options.set_capability("appium:app", config["APP"])
    else:
        options.set_capability("appium:appPackage", config["APP_PACKAGE"])
        options.set_capability("appium:appActivity", config["APP_ACTIVITY"])

    driver = webdriver.Remote(server_url, options=options)

    # Ajustes finos (menos “idle wait” y payload chico)
    driver.update_settings({
        "waitForIdleTimeout": 0,
        "ignoreUnimportantViews": True,
        "normalizeTagNames": True,
        "actionAcknowledgmentTimeout": 0,
        "scrollAcknowledgmentTimeout": 0,
        "waitForSelectorTimeout": 2000,
        "shouldUseCompactResponses": True,
        "elementResponseAttributes": "id,content-desc,text,class,index",
    })

    return driver
