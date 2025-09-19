import os
import time
import traceback

from config.config_loader import load_config
from pages.cuenta_page import CuentaPage
from utils.driver_factory import create_driver

from pages.login_page import LoginPage
from pages.carpeta_page import CarpetaPage
from pages.registro_page import RegistroPage
from pages.historia_clinica_page import Historia_clinica

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# ------------------ utilidades de espera ------------------

def _set_implicit_wait(driver, seconds: float):
    try:
        driver.implicitly_wait(seconds)
    except Exception:
        pass

def _has_active_session(driver) -> bool:
    try:
        return bool(driver and driver.session_id)
    except Exception:
        return False

def _broadcast_close_system_dialogs(driver):
    try:
        driver.execute_script("mobile: shell", {
            "command": "am",
            "args": ["broadcast", "-a", "android.intent.action.CLOSE_SYSTEM_DIALOGS"]
        })
    except Exception:
        pass

def _press_back(driver):
    try:
        # Android keycode BACK
        driver.press_keycode(4)
    except Exception:
        try:
            driver.execute_script("mobile: shell", {"command": "input", "args": ["keyevent", "4"]})
        except Exception:
            pass

def handle_anr_popup(driver):
    """
    Intenta cerrar el diálogo de ANR (System UI isn’t responding) eligiendo 'Wait/Esperar'.
    Si no se puede, envía BACK y cierra diálogos del sistema.
    """
    try:
        # Buscar botones típicos del ANR
        botones_wait = [
            # EN
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("(?i)wait")'),
            # ES
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("(?i)esperar|espera")'),
        ]
        botones_close = [
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("(?i)close app")'),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("(?i)cerrar (app|aplicación)")'),
        ]

        for by, val in botones_wait:
            els = driver.find_elements(by, val)
            if els:
                try:
                    els[0].click()
                    time.sleep(0.5)
                    return True
                except Exception:
                    pass

        # Si no hay "Wait", probamos cerrar el pop-up para recuperar el control
        for by, val in botones_close:
            els = driver.find_elements(by, val)
            if els:
                try:
                    els[0].click()
                    time.sleep(0.5)
                    return True
                except Exception:
                    pass

        # Plan B: BACK + broadcast
        _press_back(driver)
        _broadcast_close_system_dialogs(driver)
    except Exception:
        pass
    return False

class _AnyElementLocated:
    """EC que devuelve el primer elemento encontrado entre varios selectores."""
    def __init__(self, locators):
        self.locators = locators
    def __call__(self, driver):
        for by, val in self.locators:
            try:
                elems = driver.find_elements(by, val)
                if elems:
                    return elems[0]
            except Exception:
                pass
        return False

def esperar_inicio_app(driver, timeout: int = 45):
    print(f"[INFO] Esperando ancla de inicio (timeout={timeout}s) ...")
    _set_implicit_wait(driver, 0.5)

    anclas = [
        # EN
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("Sign in")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Sign in")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Log in")'),
        # ES
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Iniciar sesión")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Ingresar")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Acceder")'),
    ]

    end = time.time() + timeout
    while time.time() < end:
        # intentar cerrar ANR si aparece
        handle_anr_popup(driver)
        try:
            wait_short = WebDriverWait(driver, 2, poll_frequency=0.5)
            el = wait_short.until(_AnyElementLocated(anclas))
            time.sleep(0.3)
            print(f"[INFO] Ancla encontrada: {el}")
            return True
        except TimeoutException:
            # cerrar diálogos del sistema y seguir
            _broadcast_close_system_dialogs(driver)
    print("[WARN] No se encontró ancla de inicio dentro del timeout. Continuamos de todas formas.")
    return False

def _start_or_activate(driver, pkg: str, activity: str):
    """
    Inicia activity con W3C 'mobile: startActivity'. Si no hay activity específica,
    activa la app. Tolerante a clientes sin start_activity().
    """
    try:
        if activity and activity != "*":
            try:
                driver.execute_script("mobile: startActivity", {
                    "appPackage": pkg,
                    "appActivity": activity
                })
            except Exception:
                # fallback si el cliente expone start_activity
                try:
                    driver.start_activity(pkg, activity)  # puede no existir en tu client
                except Exception as e2:
                    print(f"[WARN] start_activity fallback: {e2}")
                    driver.activate_app(pkg)
        else:
            driver.activate_app(pkg)
    except Exception as e:
        print(f"[WARN] start/activate {pkg}: {e}")
        try:
            driver.activate_app(pkg)
        except Exception:
            pass

def _reset_app_state(driver, pkg: str, activity: str, timeout: int = 45):
    """ Limpia datos, relanza foreground, cierra diálogos y espera la pantalla inicial. """
    try:
        driver.execute_script("mobile: shell", {"command": "pm", "args": ["clear", pkg]})
    except Exception as e:
        print(f"[WARN] pm clear {pkg}: {e}")
    try:
        driver.terminate_app(pkg)
    except Exception:
        pass

    _start_or_activate(driver, pkg, activity)
    _broadcast_close_system_dialogs(driver)
    handle_anr_popup(driver)
    esperar_inicio_app(driver, timeout=timeout)

# ------------------ hooks Behave ------------------

def before_all(context):
    print("\n=== [SETUP GLOBAL] ===")
    try:
        env = os.getenv("TEST_ENV", "staging")
        context.configs = load_config(env)
        print(f"[INFO] Entorno de pruebas: {env}")

        context.DEFAULT_WAIT = int(os.getenv("WAIT_UI_SEC", "45"))

        context.driver = create_driver(context.configs)
        _set_implicit_wait(context.driver, 0.5)
        context.wait = WebDriverWait(context.driver, context.DEFAULT_WAIT)

        context.mock_sms_base_url = str(context.configs.get("MOCK_SMS_BASE_URL", os.getenv("MOCK_SMS_BASE_URL", "http://127.0.0.1:8081")))
        context.phone_old = str(context.configs.get("STAGING_PHONE_OLD", os.getenv("STAGING_PHONE_OLD", "+5491100000001")))
        context.phone_new = str(context.configs.get("STAGING_PHONE_NEW", os.getenv("STAGING_PHONE_NEW", "+5491100000002")))
        context.phone_local_no_cc = str(context.configs.get("STAGING_PHONE_LOCAL", os.getenv("STAGING_PHONE_LOCAL", "91100000001")))
        context.mail_tm_timeout = int(str(context.configs.get("MAIL_TM_TIMEOUT", os.getenv("MAIL_TM_TIMEOUT", "60"))))
        print(f"[INFO] Mock SMS URL: {context.mock_sms_base_url}")
        print(f"[INFO] Phones (old→new): {context.phone_old} → {context.phone_new}")
        print(f"[INFO] Phone local (sin +54): {context.phone_local_no_cc}")

    except Exception as e:
        print(f"[ERROR] Error en before_all: {e}")
        traceback.print_exc()
        raise

def before_scenario(context, scenario):
    print(f"\n=== [SETUP ESCENARIO] {scenario.name} ===")
    try:
        app_package = context.configs.get("APP_PACKAGE")
        app_activity = context.configs.get("APP_ACTIVITY", "*")

        if not _has_active_session(getattr(context, "driver", None)):
            context.driver = create_driver(context.configs)
            _set_implicit_wait(context.driver, 0.5)
            context.wait = WebDriverWait(context.driver, context.DEFAULT_WAIT)

        _reset_app_state(context.driver, app_package, app_activity, timeout=context.DEFAULT_WAIT)

        from utils.mailtm_client import MailTmClient
        context.mail_client = MailTmClient(timeout=context.mail_tm_timeout)
        context.login_page = LoginPage(context.driver)
        context.registro_page = RegistroPage(context.driver, context.mail_client)
        context.historia_clinica_page = Historia_clinica(context.driver, context.mail_client)
        context.carpeta_page = CarpetaPage(context.driver)
        context.cuenta_page = CuentaPage(context.driver)

    except Exception as e:
        print(f"[ERROR] before_scenario: {e}")
        traceback.print_exc()
        raise

def after_scenario(context, scenario):
    print(f"=== [TEARDOWN ESCENARIO] {scenario.name} ({scenario.status}) ===")
    # Mantener la sesión viva en CI suele ser más estable.
    pass

def after_all(context):
    print("\n=== [TEARDOWN GLOBAL] ===")
    try:
        if _has_active_session(getattr(context, "driver", None)):
            context.driver.quit()
            print("[INFO] Driver cerrado correctamente.")
    except Exception:
        pass
