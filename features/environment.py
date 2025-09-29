import os
import time
import traceback

from config.config_loader import load_config
from pages.completar_perfil_page import Completar_perfil
from utils.driver_factory import create_driver

from pages.login_page import LoginPage
from pages.carpeta_page import CarpetaPage
from pages.registro_page import RegistroPage
from pages.historia_clinica_page import Historia_clinica
from pages.cuenta_page import CuentaPage

from appium.webdriver.common.appiumby import AppiumBy

# Allure (para adjuntar screenshot si no aparece bienvenida)
try:
    import allure
    from allure_commons.types import AttachmentType
except Exception:
    allure = None
    AttachmentType = None

# Cliente de mail para OTP/códigos
from utils.mailtm_client import MailTmClient


# ------------ helpers ------------
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

def _attach_png(driver, name: str):
    if not allure:
        return
    try:
        png = driver.get_screenshot_as_png()
        allure.attach(png, name=name, attachment_type=AttachmentType.PNG)
    except Exception:
        pass

def esperar_inicio_bienvenida(driver, timeout=15):
    """
    Busca anclas típicas de bienvenida (Sign in / Log in) por text y content-desc.
    """
    print("[INFO] Esperando pantalla de bienvenida…")
    _set_implicit_wait(driver, 0)
    anchors = [
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Sign in")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("Log in")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Sign in")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Sign in")'),
    ]
    end = time.time() + timeout
    while time.time() < end:
        for by, val in anchors:
            try:
                if driver.find_elements(by, val):
                    print("[INFO] Bienvenida detectada.")
                    _set_implicit_wait(driver, 1.0)
                    return
            except Exception:
                pass
        time.sleep(0.2)
    print("[ERROR] No se encontró la bienvenida dentro del timeout.")
    _attach_png(driver, "bienvenida_no_detectada")
    _set_implicit_wait(driver, 1.0)

# ------------ hooks ------------
def before_all(context):
    print("\n=== [SETUP GLOBAL] ===")
    try:
        env = os.getenv("TEST_ENV", "staging")
        context.configs = load_config(env)
        print(f"[INFO] Entorno de pruebas: {env}")

        # timeouts/opciones que usan otras partes del framework
        context.close_after_scenario = True
        context.mail_tm_timeout = int(str(context.configs.get("MAIL_TM_TIMEOUT", os.getenv("MAIL_TM_TIMEOUT", "60"))))
    except Exception as e:
        print(f"[ERROR] Error en before_all: {e}")
        traceback.print_exc()
        raise

def before_scenario(context, scenario):
    print(f"\n=== [SETUP ESCENARIO] {scenario.name} ===")
    try:
        # ⚠️ Nuevo driver por escenario → con noReset=false en capabilities,
        # Appium hace reset de datos (pm clear) y la app abre como primera vez.
        context.driver = create_driver(context.configs)
        _set_implicit_wait(context.driver, 1.0)

        app_package = context.configs.get("APP_PACKAGE")
        if not app_package:
            raise RuntimeError("APP_PACKAGE no está definido en la configuración.")

        # Esperar pantalla de bienvenida
        esperar_inicio_bienvenida(context.driver)

        # Inicializar mail client (requerido por RegistroPage)
        context.mail_client = MailTmClient(timeout=context.mail_tm_timeout)

        # Instanciar Pages (inyectando mail_client )
        context.login_page = LoginPage(context.driver)
        context.registro_page = RegistroPage(context.driver, context.mail_client)
        context.historia_clinica_page = Historia_clinica(context.driver, context.mail_client)
        context.carpeta_page = CarpetaPage(context.driver)
        context.cuenta_page = CuentaPage(context.driver)
        context.completar_perfil_page = Completar_perfil(context.driver)

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
        if _has_active_session(getattr(context, "driver", None)):
            context.driver.quit()
            print("[INFO] Driver cerrado correctamente.")
    except Exception:
        pass
