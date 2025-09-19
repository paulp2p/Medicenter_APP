import os
import time
import traceback

from config.config_loader import load_config
from pages.cuenta_page import CuentaPage
from pages.login_page import LoginPage
from pages.carpeta_page import CarpetaPage
from pages.registro_page import RegistroPage
from pages.historia_clinica_page import Historia_clinica

from utils.driver_factory import create_driver
from appium.webdriver.common.appiumby import AppiumBy

# ---------- Utilidades de espera ----------
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

def _cerrar_dialogos_sistema(driver):
    """Cierra diálogos del sistema que puedan tapar la UI (ANR, system dialogs)."""
    try:
        # Cerrar diálogos del sistema
        driver.execute_script("mobile: shell", {
            "command": "am", "args": ["broadcast", "-a", "android.intent.action.CLOSE_SYSTEM_DIALOGS"]
        })
    except Exception:
        pass
    # Un par de BACK por si queda algo abierto
    for _ in range(2):
        try:
            driver.back()
            time.sleep(0.3)
        except Exception:
            break

def _screenshot(driver, name="pantalla_actual.png"):
    try:
        out = os.path.join(os.getenv("GITHUB_WORKSPACE", "."), name)
        driver.get_screenshot_as_file(out)
        print(f"[INFO] Screenshot guardado: {out}")
    except Exception as e:
        print(f"[WARN] No se pudo guardar screenshot: {e}")

def esperar_inicio_app(driver, timeout=None):
    """Espera a que aparezca un ancla de la pantalla de login."""
    DEFAULT_EXPLICIT = int(os.getenv("BEHAVE_DEFAULT_WAIT", "25"))
    timeout = timeout or DEFAULT_EXPLICIT
    print(f"[INFO] Esperando ancla de inicio (timeout={timeout}s)...")

    _set_implicit_wait(driver, 0.3)  # bajo para no encadenar tiempos
    fin = time.time() + timeout
    ok = False

    # Antes de buscar, intenta cerrar cualquier overlay/sistema.
    _cerrar_dialogos_sistema(driver)

    anclas = [
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Sign in")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Sign in")'),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Create account")'),
    ]
    while time.time() < fin and not ok:
        for by, val in anclas:
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
        print("[INFO] La app cargó correctamente (ancla encontrada).")
    else:
        print("[WARN] No se encontró ancla dentro del timeout. Tomo screenshot y continúo.")
        _screenshot(driver, "ancla_no_encontrada.png")

def _reset_app_state(driver, pkg: str, activity: str):
    """Limpia datos y relanza en foreground sin reinstalar."""
    try:
        driver.execute_script("mobile: shell", {"command": "pm", "args": ["clear", pkg]})
    except Exception as e:
        print(f"[WARN] pm clear {pkg}: {e}")
    try:
        driver.terminate_app(pkg)
    except Exception:
        pass
    try:
        driver.start_activity(pkg, activity)
    except Exception:
        try:
            driver.activate_app(pkg)
        except Exception as e:
            print(f"[WARN] start/activate {pkg}: {e}")

    _cerrar_dialogos_sistema(driver)
    esperar_inicio_app(driver)

# ---------- Hooks Behave ----------
def before_all(context):
    print("\n=== [SETUP GLOBAL] ===")
    try:
        env = os.getenv("TEST_ENV", "staging")
        context.configs = load_config(env)
        print(f"[INFO] Entorno de pruebas: {env}")

        # Una sola sesión para toda la suite
        context.driver = create_driver(context.configs)
        # Mantener implicit muy bajo para que no se sumen esperas
        _set_implicit_wait(context.driver, 0.3)

        # Datos auxiliares
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
            _set_implicit_wait(context.driver, 0.3)

        _cerrar_dialogos_sistema(context.driver)
        _reset_app_state(context.driver, app_package, app_activity)

        # páginas por escenario
        from utils.mailtm_client import MailTmClient
        context.mail_client = MailTmClient(timeout=context.mail_tm_timeout)
        context.login_page = LoginPage(context.driver)
        context.registro_page = RegistroPage(context.driver, context.mail_client)
        context.historia_clinica_page = Historia_clinica(context.driver, context.mail_client)
        context.carpeta_page = CarpetaPage(context.driver)
        context.cuenta_page = CuentaPage(context.driver)

    except Exception as e:
        print(f"[ERROR] before_scenario: {e}")
        _screenshot(context.driver, "before_scenario_error.png")
        traceback.print_exc()
        raise

def after_scenario(context, scenario):
    print(f"=== [TEARDOWN ESCENARIO] {scenario.name} ({scenario.status}) ===")
    # Mantener la sesión viva para estabilidad en CI
    pass

def after_all(context):
    print("\n=== [TEARDOWN GLOBAL] ===")
    try:
        if _has_active_session(getattr(context, "driver", None)):
            context.driver.quit()
            print("[INFO] Driver cerrado correctamente.")
    except Exception:
        pass
