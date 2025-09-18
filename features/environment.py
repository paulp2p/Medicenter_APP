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

# Esperas explícitas Selenium/Appium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# --------------------------------------------------------------------
# Utilidades de espera
# --------------------------------------------------------------------

def _set_implicit_wait(driver, seconds: float):
    """Evitar implícitas largas cuando usamos explícitas: mantener bajo (0–1s)."""
    try:
        driver.implicitly_wait(seconds)
    except Exception:
        pass


def _has_active_session(driver) -> bool:
    try:
        return bool(driver and driver.session_id)
    except Exception:
        return False


class _AnyElementLocated:
    """ExpectedCondition: devuelve el primer elemento encontrado entre varios selectores."""
    def __init__(self, locators):
        # locators: List[Tuple[by, value]]
        self.locators = locators

    def __call__(self, driver):
        for by, val in self.locators:
            try:
                elems = driver.find_elements(by, val)
                if elems:
                    return elems[0]
            except Exception:
                # ignoramos y probamos el siguiente
                pass
        return False


def esperar_inicio_app(driver, timeout: int = 45):
    """
    Espera explícita a que aparezca algún ancla 'estable' de la pantalla inicial.
    Usa múltiples posibles anclas (inglés/español).
    """
    print(f"[INFO] Esperando ancla de inicio (timeout={timeout}s) ...")
    # Mantener implícita muy baja para no interferir con la explícita
    _set_implicit_wait(driver, 0.5)

    anclas = [
        # Accesibility/description en inglés
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Sign in")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("Log in")'),
        # Texto en inglés
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Sign in")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Log in")'),
        # Texto en español (por si tu build muestra ES)
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Iniciar sesión")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Ingresar")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Acceder")'),
    ]

    try:
        wait = WebDriverWait(driver, timeout, poll_frequency=0.5)
        elem = wait.until(_AnyElementLocated(anclas))
        try:
            # Dar 300ms para que estabilice el árbol
            time.sleep(0.3)
        except Exception:
            pass
        print(f"[INFO] Ancla encontrada: {elem}")
        return True
    except TimeoutException:
        print("[WARN] No se encontró ancla de inicio dentro del timeout. Continuamos de todas formas.")
        return False


def _reset_app_state(driver, pkg: str, activity: str, timeout: int = 45):
    """Limpia datos sin reinstalar y relanza en foreground, luego espera la pantalla inicial."""
    try:
        driver.execute_script("mobile: shell", {"command": "pm", "args": ["clear", pkg]})
    except Exception as e:
        print(f"[WARN] pm clear {pkg}: {e}")

    try:
        driver.terminate_app(pkg)
    except Exception:
        pass

    try:
        # Si la activity es comodín '*', preferimos activate_app
        if activity and activity != "*":
            driver.start_activity(pkg, activity)
        else:
            driver.activate_app(pkg)
    except Exception as e:
        print(f"[WARN] start/activate {pkg}: {e}")
        try:
            driver.activate_app(pkg)
        except Exception:
            pass

    # Cerrar diálogos del sistema que puedan tapar la UI
    try:
        driver.execute_script("mobile: shell", {
            "command": "am", "args": ["broadcast", "-a", "android.intent.action.CLOSE_SYSTEM_DIALOGS"]
        })
    except Exception:
        pass

    # Espera a que la UI inicial esté lista
    esperar_inicio_app(driver, timeout=timeout)


# --------------------------------------------------------------------
# Hooks Behave
# --------------------------------------------------------------------

def before_all(context):
    print("\n=== [SETUP GLOBAL] ===")
    try:
        env = os.getenv("TEST_ENV", "staging")
        context.configs = load_config(env)
        print(f"[INFO] Entorno de pruebas: {env}")

        # Timeout de espera explícita centralizado (ajustable por ENV)
        context.DEFAULT_WAIT = int(os.getenv("WAIT_UI_SEC", "45"))

        # Una sola sesión para toda la suite
        context.driver = create_driver(context.configs)

        # Implícita BAJA para no interferir con explícitas
        _set_implicit_wait(context.driver, 0.5)

        # WebDriverWait global de conveniencia
        context.wait = WebDriverWait(context.driver, context.DEFAULT_WAIT)

        # Mails / datos
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

        # Limpieza ligera entre escenarios (sin reinstalar) y relanzar foreground
        _reset_app_state(context.driver, app_package, app_activity, timeout=context.DEFAULT_WAIT)

        # páginas/clientes por escenario
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
    # Mantener la sesión viva suele ser más estable en CI (emulador TCG).
    pass


def after_all(context):
    print("\n=== [TEARDOWN GLOBAL] ===")
    try:
        if _has_active_session(getattr(context, "driver", None)):
            context.driver.quit()
            print("[INFO] Driver cerrado correctamente.")
    except Exception:
        pass
