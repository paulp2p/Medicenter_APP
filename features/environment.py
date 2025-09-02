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

def _app_state_str(state: int) -> str:
    mapping = {0: "UNKNOWN", 1: "NOT_INSTALLED", 2: "NOT_RUNNING", 3: "BACKGROUND", 4: "FOREGROUND"}
    return mapping.get(state, str(state))

def esperar_inicio_app(driver, timeout=25):
    print("[INFO] Esperando a que la app cargue completamente...")
    _set_implicit_wait(driver, 0.5)
    fin = time.time() + timeout
    ok = False
    posibles_anchos = [
        # EN
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("Sign in")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Sign in")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("Log in")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Log in")'),
        # ES
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Iniciar sesión")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Ingresar")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Acceder")'),
    ]
    while time.time() < fin and not ok:
        for by, val in posibles_anchos:
            try:
                if driver.find_elements(by, val):
                    ok = True
                    break
            except Exception:
                pass
        if not ok:
            time.sleep(0.4)
    try:
        print(f"[DEBUG] pkg/act: {driver.current_package} / {driver.current_activity}")
    except Exception:
        pass
    print("[INFO] La app cargó correctamente." if ok else "[WARN] Sin ancla visible; continuamos.")

def cerrar_app_suave(driver, app_package: str, extra_log=""):
    try:
        if not _has_active_session(driver):
            print("[INFO] cerrar_app_suave: no hay sesión activa, nada que cerrar.")
            return
        estado = driver.query_app_state(app_package)
        # (si tenías lógica acá, mantenla)
    except Exception:
        pass

def activar_y_esperar(driver, app_package: str):
    print("[INFO] Activando app…")
    try:
        estado = driver.query_app_state(app_package)
        if estado != 4:
            driver.activate_app(app_package)
    except Exception:
        # Si falla query_app_state, igual intentamos activar
        try:
            driver.activate_app(app_package)
        except Exception:
            pass
    esperar_inicio_app(driver)

def _is_true(val: str, default=False) -> bool:
    if val is None:
        return default
    return str(val).strip().lower() in ("1", "true", "yes", "on")

def before_all(context):
    print("\n=== [SETUP GLOBAL] ===")
    try:
        env = os.getenv("TEST_ENV", "staging")
        context.configs = load_config(env)
        context.api_base_url = context.configs.get("API_BASE_URL")
        print(f"[INFO] Entorno de pruebas: {env}")

        # CI/Local toggles
        context.close_after_scenario = _is_true(context.configs.get("CLOSE_AFTER_SCENARIO", "true"), True)
        context.clean_start = _is_true(context.configs.get("CLEAN_START", "true"), True)

        # Datos auxiliares que tus steps podrían usar
        context.phone_old = str(context.configs.get("STAGING_PHONE_OLD", os.getenv("STAGING_PHONE_OLD", "+5491100000001")))
        context.phone_new = str(context.configs.get("STAGING_PHONE_NEW", os.getenv("STAGING_PHONE_NEW", "+5491100000002")))
        context.phone_local_no_cc = str(context.configs.get("STAGING_PHONE_LOCAL", os.getenv("STAGING_PHONE_LOCAL", "91100000001")))
        context.mail_tm_timeout = int(str(context.configs.get("MAIL_TM_TIMEOUT", os.getenv("MAIL_TM_TIMEOUT", "60"))))

        print(f"[INFO] Phones (old→new): {context.phone_old} → {context.phone_new}")
        print(f"[INFO] Phone local (sin +54): {context.phone_local_no_cc}")

        # CI: APP_PATH inyectado por workflow
        app_path = os.getenv("APP_PATH", "").strip()
        if app_path and os.path.exists(app_path):
            context.configs["APP_PATH"] = app_path
            print(f"[INFO] APP_PATH recibido (CI): {app_path}")
        else:
            print("[INFO] APP_PATH no definido o archivo no existe. Se usará appPackage/appActivity.")

        # Eliminar por completo Mock SMS
        context.mock_sms = None

    except Exception as e:
        print(f"[ERROR] Error en before_all: {e}")
        traceback.print_exc()
        raise

def before_scenario(context, scenario):
    print(f"\n=== [SETUP ESCENARIO] {scenario.name} ===")
    try:
        context.driver = create_driver(context.configs)
        _set_implicit_wait(context.driver, 1.0)

        app_package = context.configs.get("APP_PACKAGE")

        if context.clean_start:
            try:
                estado = context.driver.query_app_state(app_package)
                if estado in (3, 4):
                    print("[INFO] Clean start habilitado y app corriendo -> cerrar suave antes de iniciar.")
                    cerrar_app_suave(context.driver, app_package, extra_log=" (pre)")
            except Exception:
                pass

        activar_y_esperar(context.driver, app_package)

        # Mail y Pages
        context.mail_client = MailTmClient(timeout=context.mail_tm_timeout)
        context.login_page = LoginPage(context.driver)
        context.registro_page = RegistroPage(context.driver, context.mail_client)
        context.historia_clinica_page = Historia_clinica(context.driver, context.mail_client)
        context.carpeta_page = CarpetaPage(context.driver)
        context.cuenta_page = CuentaPage(context.driver)

    except Exception as e:
        print(f"[ERROR] before_scenario: {e}")
        traceback.print_exc()
        try:
            if getattr(context, "driver", None):
                context.driver.quit()
        except Exception:
            pass
        raise

def after_scenario(context, scenario):
    print(f"=== [TEARDOWN ESCENARIO] {scenario.name} (Status.{scenario.status}) ===")
    try:
        app_package = context.configs.get("APP_PACKAGE", "")
        if _has_active_session(getattr(context, "driver", None)) and context.close_after_scenario and app_package:
            cerrar_app_suave(context.driver, app_package, extra_log=" (post)")

        if _has_active_session(getattr(context, "driver", None)):
            context.driver.quit()
            print("[INFO] Driver cerrado correctamente.")
        else:
            print("[INFO] after_scenario: no había sesión activa que cerrar.")
    except Exception:
        pass
