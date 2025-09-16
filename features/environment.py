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

from selenium.common.exceptions import NoSuchElementException
from appium.webdriver.common.appiumby import AppiumBy

from utils.mailtm_client import MailTmClient
from behave.model_core import Status


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

def esperar_inicio_app(driver, timeout=25):
    print("[INFO] Esperando a que la app cargue completamente...")
    _set_implicit_wait(driver, 0.5)
    fin = time.time() + timeout
    ok = False
    posibles_anchos = [
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Sign in")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("Log in")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Sign in")'),
    ]
    while time.time() < fin and not ok:
        for by, val in posibles_anchos:
            try:
                elems = driver.find_elements(by, val)
                if elems:
                    ok = True
                    break
            except Exception:
                pass
        if not ok:
            time.sleep(0.4)
    if ok:
        print("[INFO] La app cargó correctamente.")
    else:
        print("[WARN] No se encontró ancla de inicio dentro del timeout. Continuamos de todas formas.")

def _reset_app_state(driver, pkg: str, activity: str):
    """
    Limpia datos de la app sin reinstalar y la relanza en foreground.
    Requiere que el workflow exporte: NO_RESET=true y ENFORCE_APP_INSTALL=false
    """
    # borra datos
    try:
        driver.execute_script("mobile: shell", {"command": "pm", "args": ["clear", pkg]})
    except Exception as e:
        print(f"[WARN] pm clear {pkg}: {e}")

    # terminar si quedó viva
    try:
        driver.terminate_app(pkg)
    except Exception:
        pass

    # relanzar
    try:
        driver.start_activity(pkg, activity)
    except Exception:
        try:
            driver.activate_app(pkg)
        except Exception as e:
            print(f"[WARN] start/activate {pkg}: {e}")

    esperar_inicio_app(driver)


def before_all(context):
    print("\n=== [SETUP GLOBAL] ===")
    try:
        env = os.getenv("TEST_ENV", "staging")
        context.configs = load_config(env)
        context.api_base_url = context.configs.get("API_BASE_URL")
        print(f"[INFO] Entorno de pruebas: {env}")

        # Crear UNA sola sesión para toda la suite
        context.driver = create_driver(context.configs)
        _set_implicit_wait(context.driver, 1.0)

        # Correos / datos de entorno
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
            # fallback por si se cerró por fuera
            context.driver = create_driver(context.configs)

        # Limpieza ligera entre escenarios (sin reinstalar)
        _reset_app_state(context.driver, app_package, app_activity)

        # clientes/páginas por escenario
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
    print(f"=== [TEARDOWN ESCENARIO] {scenario.name} (Status.{scenario.status}) ===")
    # mantenemos la sesión viva para el siguiente escenario (más estable en CI)
    pass


def after_all(context):
    print("\n=== [TEARDOWN GLOBAL] ===")
    try:
        if _has_active_session(getattr(context, "driver", None)):
            context.driver.quit()
            print("[INFO] Driver cerrado correctamente.")
    except Exception:
        pass
