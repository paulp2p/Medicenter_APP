from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.funciones import Funciones
from utils.val_locator import Localizadores as vl
import time
DEFAULT_WAIT = 10

class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, DEFAULT_WAIT)
        self.funciones = Funciones(driver)

    # -------- Pantalla de inicio ------
    def validar_pantalla_de_inicio(self):
        # Mantengo tus validaciones pero sin sleeps; delego timing a Funciones/esperas
        self.funciones.click_y_screenshot_por_UIAUTOMATOR(vl.SLICE_1, "Digitize your health")
        self.funciones.click_y_screenshot_por_UIAUTOMATOR(vl.SLICE_2, "Share your health via QR")
        self.funciones.click_y_screenshot_por_UIAUTOMATOR(vl.SLICE_3, "Your health up to date")
        self.funciones.click_y_screenshot_por_UIAUTOMATOR(vl.SLICE_4, "Create accounts for your minor children")

    def presionar_sign_in(self):
        self.funciones.clickear_por_uiautomator('new UiSelector().description("Sign in")', "boton SIGN IN")

    def validar_ingreso_a_pantalla_login(self):
        el = self.wait.until(EC.presence_of_element_located((AppiumBy.XPATH, vl.IMG_MC_APP_LOGIN)))
        self.funciones.tomar_screenshot("validacion de pantalla login medicenter")
        return bool(el)

    # -------- Login acciones --------
    def ingresar_usuario(self, usuario):
        time.sleep(0.5)
        self.funciones.escribir_por_uiautomator(vl.CAMPO_USER, usuario)

    def ingresar_clave(self, clave):
        time.sleep(0.5)
        self.funciones.escribir_por_uiautomator(vl.CAMPO_PASSW, clave)

    def presionar_btn_login(self):
        self.funciones.validar_y_clickear_por_xpath(vl.BTN_SIGN_IN, "boton LOGIN")

    def borrar_credenciales(self):
        # Evito sleeps, delego a util que borra con teclado
        self.funciones.borrar_input_con_teclado('new UiSelector().text("lromano")')
        self.funciones.borrar_input_con_teclado('new UiSelector().text("********")')

    def cerrar_sesion(self):
        self.funciones.clickear_por_uiautomator(vl.BTN_PERFIL)
        self.funciones.clickear_por_uiautomator(vl.BTN_LOGOUT, "click en boton de LOGOUT")
        self.funciones.clickear_por_uiautomator(vl.BTN_OK_LOGOUT, "click en boton de LOGOUT")

    def login_desde_centro_de_cuentas(self):
        self.funciones.clickear_por_uiautomator('new UiSelector().description("Sign in")', "click boton sign in")
        self.funciones.escribir_por_uiautomator('new UiSelector().className("android.widget.EditText")', "Test12345")
        self.funciones.capturar_imagen_por_xpath(vl.IMG_LOGO, "validacion de ingreso por centro de cuentas")
        self.funciones.clickear_por_xpath('//android.widget.Button[@content-desc="Log in"]', "boton login centro de cuentas")

    def cerrar_apk(self):
        self.funciones.cerrar_app()

    # -------- Login Exitoso Sin Identidad Validada --------
    def validar_header(self):
        descripcion = self.funciones.obtener_content_desc_por_uiautomator("Complete your profile", "header_contenido_extraido")
        print(descripcion)

    # -------- Login validaciones ------
    def valida_ingreso(self):
        self.funciones.capturar_imagen_por_xpath(vl.IMG_LOGEADO, "validacion de pantalla login")

    def usuario_invalido(self):
        return self.funciones.capturar_imagen_por_xpath(vl.INVALID_USER, "validacion de mensaje de error - USUARIO INVALIDO")

    def clave_invalido(self):
        return self.funciones.capturar_imagen_por_xpath(vl.INVALID_PASSW, "validacion de mensaje de error - CLAVE INVALIDO")

    # -------- Login desde Ingresar con otra cuenta --------
    def iniciar_sesion_con_otra_cuenta(self):
        self.funciones.validar_y_clickear_por_uiautomator(vl.BTN_OTRA_CUENTA, "boton otra cuenta")
