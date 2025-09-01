from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.funciones import Funciones
from utils.val_locator import Localizadores as vl
from utils.mailtm_client import MailTmClient  # <-- ajustar si tu módulo se llama distinto
from utils.mail_helpers import obtener_codigo_de_mail_guardado
from faker import Faker
import os
import time

t = 3


class RegistroPage:
    def __init__(self, driver, mail_client):
        self.driver = driver
        self.wait = WebDriverWait(driver, 60)
        self.funciones = Funciones(driver)
        self.mail_client = mail_client
        self.faker = Faker('es_ES')

    # --- Helpers ----------------------------------------------------------------
    def _ensure_mail_ready(self, timeout=60):
        """
        Garantiza que self.mail_client exista y tenga un address utilizable.
        Si no existe, lo crea. Si existe pero no tiene address, crea cuenta.
        """
        if self.mail_client is None:
            # Crea cliente con auto_create=True => cuenta+token+address listo
            self.mail_client = MailTmClient(timeout=timeout)
        else:
            # Si hay cliente pero no address, aseguramos cuenta lista
            if not getattr(self.mail_client, "address", None):
                # Compatibilidad con ambas firmas
                if hasattr(self.mail_client, "ensure_account_ready"):
                    self.mail_client.ensure_account_ready()
                elif hasattr(self.mail_client, "create_account"):
                    self.mail_client.create_account()
                else:
                    raise RuntimeError(
                        "Mail client presente pero no tiene métodos para preparar la cuenta."
                    )

        # Defensa extra
        if not getattr(self.mail_client, "address", None):
            raise RuntimeError("No se pudo obtener un email temporal (address).")

    # --- Flujo de registro -------------------------------------------------------
    # Ingresar a crear cuenta y validar pantalla de campos input
    def ingresar_create_account(self):
        self.funciones.validar_y_clickear_por_xpath(vl.CREATE_ACCOUNT)
        self.funciones.validar_elemento_presente_uiautomator(vl.TEXTO_PANTALLA_REGISTRO)

    def ingresar_datos(self):
        # Asegura email temporal listo antes de escribir
        self._ensure_mail_ready(timeout=60)

        time.sleep(2)
        email_temporal = self.mail_client.address
        nombre = self.faker.first_name()
        apellido = self.faker.last_name()
        nombre_completo = f"{nombre}{apellido}"[:12]

        # Guardar username generado
        ruta = "datos_generados/username.txt"
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(nombre_completo)

        # Completar formulario
        self.funciones.escribir_por_uiautomator(vl.CREATE_EMAIL, email_temporal)
        self.funciones.escribir_por_uiautomator(vl.CREATE_USERNAME, nombre_completo)
        self.funciones.escribir_por_uiautomator(vl.CREATE_PASSW, "Test1234")
        self.funciones.escribir_por_uiautomator(vl.CREATE_PASSW_CONFIRM, "Test1234")

    def check_y_next(self):
        self.funciones.clickear_por_uiautomator(vl.TEXTO_PANTALLA_REGISTRO)
        self.funciones.clickear_por_uiautomator(vl.CHECK_BOX_CONDITIONS)
        self.funciones.clickear_por_uiautomator(vl.BTN_NEXT)

    def reenviar_codigo(self):
        time.sleep(59)
        self.funciones.clickear_por_uiautomator(vl.RESEND_CODE)
        time.sleep(30)

    @staticmethod
    def obtener_email_guardado():
        ruta = "datos_generados/username.txt"
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read().strip()

    def obtener_codigo_verificacion(self):
        # Asegurar que el mail client esté listo por si este método se usa de forma aislada
        self._ensure_mail_ready(timeout=60)

        print("[INFO] Esperando email de verificación...")
        # Si querés filtrar por asunto, podés pasar subject_filter="verification" o similar
        mensaje = self.mail_client.wait_for_email(timeout=30)
        print(f"[INFO] Email recibido: {mensaje.get('subject')}")

        texto = self.mail_client.get_message_text(mensaje["id"])
        print(f"[DEBUG] Contenido del mensaje:\n{texto}")

        codigo = self.mail_client.extract_code_from_message(texto)
        if codigo:
            print(f"[INFO] Código de verificación extraído: {codigo}")
            return codigo
        else:
            raise Exception("[ERROR] No se encontró un código de verificación.")

    def ingresar_codigo_verificacion(self, codigo):
        time.sleep(t)
        campos_codigo = [vl.CODIGO_1, vl.CODIGO_2, vl.CODIGO_3, vl.CODIGO_4]
        if len(codigo) != 4:
            raise ValueError(f"[ERROR] El código debería tener 4 dígitos, pero se recibió: {codigo}")

        for i, digito in enumerate(codigo):
            self.funciones.escribir_por_uiautomator(campos_codigo[i], digito)
            time.sleep(0.5)
        self.funciones.tomar_screenshot("codigo_verificacion_ingresado")
        self.funciones.clickear_por_uiautomator(vl.BTN_NEXT)

    def validar_codigo_verificacion(self):
        self.funciones.validar_elemento_presente_uiautomator(vl.LOGO_MC_APP)
        self.funciones.tomar_screenshot("validar codigo verificacion ingresado fue exitoso")

    # --- Métodos individuales (opcionales) --------------------------------------
    def ingresar_email(self):
        self.funciones.escribir_por_uiautomator(vl.CREATE_EMAIL, "usuario@test.com")
        self.funciones.clickear_por_uiautomator(vl.TEXTO_PANTALLA_REGISTRO)

    def ingresar_username(self):
        self.funciones.escribir_por_uiautomator(vl.CREATE_USERNAME, "UsuarioTest")
        time.sleep(0.5)
        self.funciones.clickear_por_uiautomator(vl.TEXTO_PANTALLA_REGISTRO)

    def ingresar_password(self):
        self.funciones.escribir_por_uiautomator(vl.CREATE_PASSW, "1234567890")
        time.sleep(0.5)
        self.funciones.clickear_por_uiautomator(vl.TEXTO_PANTALLA_REGISTRO)

    def ingresar_password_confirmar(self):
        self.funciones.escribir_por_uiautomator(vl.CREATE_PASSW_CONFIRM, "1234567890")
        time.sleep(0.5)
        self.funciones.clickear_por_uiautomator(vl.TEXTO_PANTALLA_REGISTRO)

    def click_check_box(self):
        self.funciones.clickear_por_uiautomator(vl.CHECK_BOX_CONDITIONS)
        time.sleep(0.5)
        self.funciones.clickear_por_uiautomator(vl.TEXTO_PANTALLA_REGISTRO)

    def click_btn_next(self):
        self.funciones.clickear_por_uiautomator(vl.BTN_NEXT)
        time.sleep(0.5)
        self.funciones.validar_n_mensajes_required_field(cantidad_esperada=3)

    def click_btn_next2(self):
        self.funciones.clickear_por_uiautomator(vl.BTN_NEXT)
        time.sleep(0.5)
        self.funciones.tomar_screenshot("mensaje de campos obligatorios")

    def click_btn_back(self):
        self.funciones.clickear_por_uiautomator(vl.BTN_BACK)

    def volver_a_crear_cuenta(self):
        self.funciones.clickear_por_xpath(vl.CREATE_ACCOUNT)

    def presionar_sign_in(self):
        self.funciones.validar_y_clickear_por_xpath(vl.BTN_SIGN_IN, "boton SIGN IN")

    def ingresar_username_validar_perfil(self):
        usuario = self.obtener_email_guardado()  # en realidad guarda "username"; nombre heredado
        self.funciones.escribir_por_uiautomator(vl.CAMPO_USER, usuario)
        self.funciones.escribir_por_uiautomator(vl.CAMPO_PASSW, "Test1234")
        self.funciones.clickear_por_uiautomator('new UiSelector().description("Log in")')

    def ingresar_codigo_de_seguridad(self):
        codigo = obtener_codigo_de_mail_guardado(timeout=60)
        time.sleep(t)
        campos_codigo = [vl.CODIGO_1, vl.CODIGO_2, vl.CODIGO_3, vl.CODIGO_4]
        if len(codigo) != 4:
            raise ValueError(f"[ERROR] El código debería tener 4 dígitos, pero se recibió: {codigo}")

        for i, digito in enumerate(codigo):
            self.funciones.escribir_por_uiautomator(campos_codigo[i], digito)
            time.sleep(0.5)
        self.funciones.tomar_screenshot("codigo_verificacion_ingresado")
        self.funciones.clickear_por_uiautomator(vl.BTN_NEXT)

    def entrar_en_completar_perfil(self):
        try:
            self.funciones.clickear_por_xpath(vl.H_PROFILE)
            self.funciones.clickear_por_uiautomator(vl.BTN_STAR)
            print("[INFO] Esperando BTN_GO_TO_HOME o BTN_ACTION_PRIMARY…")

            btn_home = None
            try:
                btn_home = self.wait.until(
                    EC.presence_of_element_located(
                        (AppiumBy.ANDROID_UIAUTOMATOR, vl.BTN_GO_TO_HOME)
                    )
                )
                if btn_home.is_displayed():
                    btn_home.click()
                    print("[INFO] BTN_GO_TO_HOME clickeado.")
                    return True
            except Exception:
                print("[WARN] BTN_GO_TO_HOME no visible, intentando BTN_ACTION_PRIMARY…")

            self.funciones.clickear_por_uiautomator(vl.BTN_ACTION_PRIMARY, "botón Siguiente")
            print("[INFO] BTN_ACTION_PRIMARY clickeado.")
            return True

        except Exception as e:
            self.funciones.tomar_screenshot("error_en_completar_perfil")
            print(f"[ERROR] Fallo en entrar_en_completar_perfil: {e}")
            raise

    def select_region(self):
        campo_pais = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((
            AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("com.siltium.medicenter:id/tvSelectedCountry")')))
        campo_pais.click()

        pais_argentina = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((
            AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Argentina")')))
        pais_argentina.click()

    def select_documento_de_identidad(self):
        self.funciones.clickear_por_uiautomator(vl.SELECT_DNI_EXTRANJERO)
        self.funciones.clickear_por_uiautomator(vl.BTN_ACTION_PRIMARY)
        self.funciones.clickear_por_uiautomator(vl.BTN_ACTION_SECUNDARY)
        time.sleep(0.5)
        self.funciones.clickear_por_uiautomator(vl.DNI_FRENTE, "DNI")

    def subir_dni(self):
        self.funciones.clickear_por_uiautomator(vl.DNI_FRENTE, "DNI")
        self.funciones.validar_y_clickear_por_uiautomator(vl.YES_UPLOAD, "cargando el documento")

    def validar_alerta_de_campos_obligatorios(self):
        self.funciones.validar_n_mensajes_required_field(cantidad_esperada=4)
        self.funciones.tomar_screenshot("mensaje de campos obligatorios")
    
    def escribir_mail_invalido(self):
        self.funciones.escribir_por_uiautomator(vl.CREATE_EMAIL, 'email_invalido.com)')

    def verificar_mensaje_mail_invalido(self):
        self.funciones.validar_elemento_presente_uiautomator('new UiSelector().description("Invalid e-mail")')
        self.funciones.tomar_screenshot("mensaje de email invalido")

    def reingresar_a_seccion_crear_cuenta(self):
        self.funciones.clickear_por_uiautomator('new UiSelector().description("Back")')
        self.funciones.clickear_por_xpath(vl.CREATE_ACCOUNT)
        
    def ingresar_clave_invalida(self):
        self.funciones.escribir_por_uiautomator(vl.CREATE_PASSW, 'test1234')
        self.funciones.clickear_por_uiautomator(vl.TEXTO_PANTALLA_REGISTRO)
        self.funciones.clickear_por_uiautomator(vl.CHECK_BOX_CONDITIONS)
        self.funciones.clickear_por_uiautomator(vl.BTN_NEXT)
        
    def verificar_mensaje_clave_invalida(self):
        self.funciones.validar_elemento_presente_uiautomator('new UiSelector().description("Password must contain at least 1 uppercase.")')
        self.funciones.tomar_screenshot("la clave debe contener al menos 1 mayuscula")