from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.funciones import Funciones
from utils.val_locator import Localizadores as vl
import time
import os
import random

class CuentaPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)
        self.funciones = Funciones(driver)
        self._ultimo_numero_local = None  # sin +54

    @staticmethod
    def _solo_digitos(s: str) -> str:
        return "".join(ch for ch in str(s) if ch.isdigit())

    # --------  ------
    def click_boton_cuenta(self):
        self.funciones.clickear_por_uiautomator(vl.NAV_CUENTA)

    # ------------------------------------------------------------- editar_username
    def editar_username_de_informacion_de_cuenta(self):
        self.funciones.clickear_por_uiautomator('new UiSelector().className("android.widget.ImageView").instance(6)')
        self.funciones.borrar_input_con_teclado('new UiSelector().text("danielruiz")')
        self.funciones.escribir_por_uiautomator('new UiSelector().className("android.widget.EditText").instance(0)', "grelbelgrano")
        self.funciones.clickear_por_uiautomator('new UiSelector().description("Save changes")')
        time.sleep(1)

    def validar_userneme(self):
        self.funciones.capturar_imagen_por_uiautomator('new UiSelector().description("Username:")', 'cambio de username')

    def volver_al_username_original(self):
        self.funciones.clickear_por_uiautomator('new UiSelector().className("android.widget.ImageView").instance(6)')
        self.funciones.borrar_input_con_teclado('new UiSelector().text("grelbelgrano")')
        self.funciones.escribir_por_uiautomator('new UiSelector().className("android.widget.EditText").instance(0)', "danielruiz")
        self.funciones.clickear_por_uiautomator('new UiSelector().description("Save changes")')

    # ------------------------------------------------------------- 
    def editar_email_de_informacion_de_cuenta(self):
        self.funciones.clickear_por_uiautomator('new UiSelector().className("android.widget.ImageView").instance(6)')
        self.funciones.esperar_elemento_visible('new UiSelector().description("Edit account information")', timeout=6)
        self.funciones.borrar_input('new UiSelector().text("blussp@gmail.com")')
        self.funciones.escribir_por_uiautomator('new UiSelector().className("android.widget.EditText").instance(1)', "test1@gmail.com")
        self.funciones.clickear_por_uiautomator('new UiSelector().description("Save changes")')

    def validar_email(self):
        time.sleep(1)
        self.funciones.capturar_imagen_por_uiautomator('new UiSelector().description("E-mail address:")', 'cambio de email')

    # ------------------------------------------------------------- 
    def editar_email_en_informacion_de_cuenta(self):
        time.sleep(1)
        self.funciones.click_por_coordenadas(960, 590)
        time.sleep(1)
        self.funciones.borrar_input_con_teclado('new UiSelector().text("blussp@gmail.com")')
        self.funciones.escribir_por_uiautomator('new UiSelector().className("android.widget.EditText").instance(1)', "test@mail.com")
        self.funciones.clickear_por_uiautomator('new UiSelector().description("Save changes")')

    def validar_cambio_email(self):
        time.sleep(1)
        self.funciones.validar_elemento_presente_uiautomator('You need to validate the e-mail address')
        self.funciones.clickear_por_xpath('//android.view.View[@content-desc="Edit account information"]')
        self.funciones.clickear_por_xpath('//android.widget.Button[@content-desc="Ok"]')

    # ------------------------------------------------------------- 
    def opciones_de_foto_perfil(self):
        self.funciones.clickear_por_uiautomator('new UiSelector().className("android.widget.ImageView").instance(6)')
        self.funciones.esperar_elemento_visible('new UiSelector().description("Edit account information")', timeout=6)
        self.funciones.click_por_coordenadas(300, 500)
        time.sleep(2)
        self.funciones.click_por_coordenadas(200, 2080)
        time.sleep(2)
        self.funciones.clickear_por_xpath('//android.widget.ImageView[@resource-id="com.google.android.documentsui:id/icon_thumb"]','imagen selecionada')
        time.sleep(2)
        self.funciones.click_por_coordenadas(1010, 200)

    def validar_cambio_de_nueva_imagen_de_perfil(self):
        time.sleep(0.5)
        self.funciones.tomar_screenshot('cambio de imagen de perfil')
        self.funciones.clickear_por_uiautomator('new UiSelector().description("Save changes")')
        time.sleep(0.5)

    # ------------------------------------------------------------- 
    def eliminar_imagen_de_perfil(self):
        self.funciones.clickear_por_uiautomator('new UiSelector().className("android.widget.ImageView").instance(6)')
        time.sleep(2)
        self.funciones.click_por_coordenadas(300, 500)
        self.funciones.esperar_elemento_visible('//android.widget.Button[@content-desc="Crop"]', timeout=6)
        self.funciones.click_por_coordenadas(280, 2090)
        self.funciones.esperar_elemento_visible('new UiSelector().description("Save changes")', 6)
        self.funciones.clickear_por_uiautomator('new UiSelector().description("Save changes")')

    def screen_shot_imagen_de_perfil(self):
        self.funciones.esperar_elemento_visible(AppiumBy.XPATH, '//android.widget.ScrollView/android.widget.ImageView[1]', 6, 'imagen de perfil eliminada')

    # ------------------------------------------------------------- 
    def campos_obligatorios(self):
        self.funciones.clickear_por_uiautomator('new UiSelector().className("android.widget.ImageView").instance(6)')
        self.funciones.esperar_elemento_visible('new UiSelector().description("Edit account information")', timeout=6)
        self.funciones.borrar_input_con_teclado('new UiSelector().text("danielruiz")')
        self.funciones.borrar_input_con_teclado('new UiSelector().text("blussp@gmail.com")')
        time.sleep(0.5)
        self.funciones.clickear_por_uiautomator('new UiSelector().description("Save changes")')

    def validar_mensaje_alerta_de_campos_obligatorios(self):
        time.sleep(0.5)
        self.funciones.esperar_elemento_visible(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Required field").instance(0)', 3, 'alerta campo usuario requerido')
        self.funciones.esperar_elemento_visible(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Required field").instance(1)', 3, 'alerta campo mail requerido')
        self.funciones.clickear_por_uiautomator('new UiSelector().description("Edit account information")')
        self.funciones.clickear_por_xpath('//android.widget.Button[@content-desc="Ok"]')

    # ------------------------------------------------------------- 
    def cambiar_nro_telefono(self, numero_local: str, mock_sms=None, hacer_flush=True):
        """Cambia el número (SIN +54), selecciona AR y dispara Verify."""
        self._ultimo_numero_local = self._solo_digitos(numero_local)

        # Abrir edición
        self.funciones.clickear_por_uiautomator('new UiSelector().className("android.widget.ImageView").instance(6)')
        time.sleep(2)

        # País AR
        self.funciones.click_por_coordenadas(180, 1080)
        self.funciones.escribir_por_uiautomator('new UiSelector().className("android.widget.EditText")', 'arg')
        time.sleep(1)
        # Preferimos un locator estable; si no existe, cae al tap por coordenadas
        if not self.funciones.clickear_por_xpath('//android.widget.ImageView[@content-desc="+ AR Argentina"]'):
            self.funciones.click_por_coordenadas(170, 400)

        # Número SIN +54
        self.funciones.escribir_por_uiautomator('new UiSelector().className("android.widget.EditText").instance(1)', self._ultimo_numero_local)

        # Flush previo
        if mock_sms and hacer_flush:
            try:
                mock_sms.flush(f"+54{self._ultimo_numero_local}")
                if self._ultimo_numero_local.startswith("9"):
                    mock_sms.flush(f"+54{self._ultimo_numero_local[1:]}")
            except Exception:
                pass

        # Disparar OTP (XPath)
        self.funciones.clickear_por_xpath('//android.view.View[@content-desc="Verify"]')

        # Esperar que aparezca el primer input del OTP
        self.funciones.esperar_elemento_visible('new UiSelector().className("android.widget.EditText").instance(0)', timeout=10)

    def esperar_y_ingresar_otp_4(self, mock_sms, timeout=180, poll=3):
        """
        Espera OTP de 4 dígitos desde el mock y lo ingresa en los inputs
        android.widget.EditText.instance(0..3). Devuelve (otp, to_usado, data).
        Incluye auto-send al mock (controlado por AUTO_SEND_TO_MOCK).
        """
        if not self._ultimo_numero_local:
            raise AssertionError("No hay número local previo. Llamá primero a cambiar_nro_telefono().")

        local = self._ultimo_numero_local
        candidatos = [f"+54{local}"] + ([f"+54{local[1:]}"] if local.startswith("9") else [])

        # --- AUTO-SEND ---
        auto = os.getenv("AUTO_SEND_TO_MOCK", "1").lower() in ("1","true","yes","on")
        otp_fixed = os.getenv("STAGING_FIXED_OTP")
        otp_to_send = otp_fixed if (otp_fixed and otp_fixed.isdigit() and len(otp_fixed) == 4) else f"{random.randint(0,9999):04d}"
        if auto:
            try:
                txt = f"Tu código es {otp_to_send}"
                for cand in candidatos:
                    r = mock_sms.send(cand, txt)
                    print(f"[AUTO-SEND] /send to={cand} text='{txt}' -> {r}")
                print(f"[AUTO-SEND] OTP ENVIADO={otp_to_send}")
                time.sleep(0.5)
            except Exception as e:
                print(f"[AUTO-SEND][ERROR] {e}")

        print(f"[OTP] Esperando OTP(4) para {candidatos} (timeout={timeout}s, poll={poll}s)")
        # ... resto de la función igual (polling + escritura en inputs) ...

        # ----- Polling al mock -----
        otp, to_usado, data = None, None, None
        try:
            if hasattr(mock_sms, "wait_otp_candidates"):
                otp, to_usado, data = mock_sms.wait_otp_candidates(candidatos, timeout=timeout, poll=poll, otp_len=4)
            else:
                for cand in candidatos:
                    otp = mock_sms.wait_otp(cand, timeout=timeout, poll=poll, otp_len=4)
                    if otp:
                        to_usado = cand
                        try:
                            data = mock_sms.last(cand)
                        except Exception:
                            data = {"ok": True, "text": None}
                        break
        except Exception as e:
            print(f"[OTP][ERROR] Falla consultando mock: {e}")

        if data:
            txt = data.get("text")
            key = data.get("key")
            print(f"[OTP] Respuesta mock: ok={data.get('ok')} key={key} to_usado={to_usado} text='{txt}'")
        print(f"[OTP] OTP recibido: {otp!r}")

        assert otp, f"No llegó OTP (4 dígitos) para {candidatos} en el tiempo esperado."

        # ----- Ingreso del OTP -----
        try:
            inputs = self.driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.EditText")')
            visibles = [el for el in inputs if (el.is_displayed() or el.is_enabled())]
            print(f"[OTP] EditText encontrados: total={len(inputs)} visibles={len(visibles)}")
        except Exception as e:
            print(f"[OTP][WARN] No se pudieron listar los EditText: {e}")
            visibles = []

        # A) 4 inputs (uno por dígito)
        if len(visibles) >= 4:
            for i, d in enumerate(otp[:4]):
                ui = f'new UiSelector().className("android.widget.EditText").instance({i})'
                print(f"[OTP] -> digit[{i}]='{d}' en {ui}")
                try:
                    el = self.funciones.esperar_elemento_visible(ui, timeout=8)
                    if not el:
                        el = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui)
                    el.click()
                    el.send_keys(d)
                except Exception as e:
                    print(f"[OTP][ERROR] No pude escribir dígito {i}='{d}': {e}")
                    try:
                        self.driver.switch_to.active_element.send_keys(d)
                        print(f"[OTP][INFO] digit[{i}] enviado al elemento activo (fallback).")
                    except Exception as e2:
                        print(f"[OTP][ERROR] Fallback active_element también falló: {e2}")
                        raise

        # B) 1 input (OTP completo)
        elif len(visibles) == 1:
            print("[OTP] Solo 1 input visible: envío OTP completo.")
            try:
                el = visibles[0]; el.click(); el.send_keys(otp)
            except Exception as e:
                print(f"[OTP][ERROR] No pude escribir OTP completo en único input: {e}")
                raise

        # C) No visibles -> intentar por instance(i)
        else:
            print("[OTP][WARN] No encontré 4 inputs visibles. Intento por instance(0..3) igualmente.")
            for i, d in enumerate(otp[:4]):
                ui = f'new UiSelector().className("android.widget.EditText").instance({i})'
                try:
                    el = self.funciones.esperar_elemento_visible(ui, timeout=6)
                    if not el:
                        continue
                    el.click(); el.send_keys(d)
                    print(f"[OTP] digit[{i}] escrito por fallback instance().")
                except Exception as e:
                    print(f"[OTP][WARN] No pude escribir digit[{i}] por fallback: {e}")

        # Intentar “Next” (si existe)
        try:
            print("[OTP] Intentando presionar 'Next'…")
            self.funciones.tomar_screenshot("otp_before_next")
            self.funciones.clickear_por_xpath('//android.widget.Button[@content-desc="Next"]', nombre_screenshot="otp_next")
        except Exception as e:
            print(f"[OTP][WARN] No se pudo presionar 'Next': {e}")

        print(f"[OTP] Ingreso finalizado. OTP='{otp}' (to_usado={to_usado})")
        return otp, to_usado, data
    
        """press_next = os.getenv("PRESS_NEXT_AFTER_OTP", "1").lower() in ("1","true","yes","on")

        if press_next:
            try:
                print("[OTP] Intentando presionar 'Next'…")
                self.funciones.tomar_screenshot("otp_before_next")
                self.funciones.clickear_por_xpath('//android.widget.Button[@content-desc="Next"]', nombre_screenshot="otp_next")
            except Exception as e:
                print(f"[OTP][WARN] No se pudo presionar 'Next': {e}")
        else:
            print("[OTP] PRESS_NEXT_AFTER_OTP=0 -> no presiono Next (evito validación del backend).")
"""
        
