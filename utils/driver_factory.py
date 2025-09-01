from appium import webdriver
from appium.options.android import UiAutomator2Options

def create_driver(config):
    # URL del servidor Appium (permite override por config)
    server_url = config.get("APPIUM_SERVER_URL", "http://127.0.0.1:4723")

    options = UiAutomator2Options()
    options.set_capability("platformName", config.get("PLATFORM_NAME", "Android"))
    options.set_capability("appium:automationName", config.get("AUTOMATION_NAME", "UiAutomator2"))
    options.set_capability("appium:deviceName", config["DEVICE_NAME"])

    options.set_capability("appium:autoGrantPermissions", True)
    options.set_capability("appium:newCommandTimeout", int(config.get("NEW_COMMAND_TIMEOUT", 120)))
    options.set_capability("appium:noReset", str(config.get("NO_RESET", "False")).lower() == "true")
    options.set_capability("appium:fullReset", str(config.get("FULL_RESET", "False")).lower() == "true")
    options.set_capability("appium:disableWindowAnimation", True)
    options.set_capability("appium:appWaitActivity", config.get("APP_WAIT_ACTIVITY", "*"))

    if config.get("UDID"):
        options.set_capability("appium:udid", config["UDID"])

    if config.get("APP"):
        options.set_capability("appium:app", config["APP"])
    else:
        options.set_capability("appium:appPackage", config["APP_PACKAGE"])
        options.set_capability("appium:appActivity", config["APP_ACTIVITY"])

    return webdriver.Remote(server_url, options=options)
