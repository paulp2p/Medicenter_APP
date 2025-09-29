from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.funciones import Funciones
from utils.val_locator import Localizadores as vl
import time


class Completar_perfil:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.funciones = Funciones(driver)

    # eliminar cuenta - eliminar datos previos #######################
    def entrar_a_cuenta(self):
        self.funciones.clickear_por_uiautomator('new UiSelector().description("Account")')

    def eliminar_cuenta(self):
        self.funciones.scroll_hasta_elemento('new UiSelector().description("Delete account")')
        self.funciones.clickear_por_uiautomator('new UiSelector().description("Delete account")')
        # popup eliminar cuenta
        self.funciones.clickear_por_uiautomator('new UiSelector().description("Yes, delete")')

    # este paso viene despues de inicar sesion nuevamente con la cuenta eliminada
    def go_to_home(self):
        self.funciones.clickear_por_uiautomator('new UiSelector().description("Go to home")')

    # completar perfil 2/5 a 3/5 #######################
    def entrar_a_completar_perfil2(self, timeout=3):
        d = self.driver
        wait = WebDriverWait(d, timeout)
        # 1) Robustez: evita el % y los \n usando descriptionContains + fallback por XPath.
        candidatos = [
            (AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().descriptionContains("2/5").descriptionContains("Complete your profile")'),
            (AppiumBy.XPATH,
            '//*[contains(@content-desc,"2/5") and contains(@content-desc,"Complete your profile")]'),
            # Si el progreso cambió, matchea cualquier n/5 + el texto:
            (AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().descriptionMatches("(?s).*[1-5]/5.*Complete\\s+your\\s+profile.*")'),
        ]
        el = None
        for by, sel in candidatos:
            try:
                el = wait.until(lambda drv: drv.find_element(by, sel))
                break
            except Exception:
                pass

        if el is None:
            try:
                scroll = ('new UiScrollable(new UiSelector().scrollable(true))'
                        '.scrollIntoView(new UiSelector().descriptionContains("Complete your profile"))')
                el = d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, scroll)
            except Exception:
                # evidencia y corta
                try:
                    self.funciones.tomar_screenshot("no_element_completar_perfil")
                finally:
                    raise
        try:
            d.execute_script("mobile: clickGesture", {"elementId": el.id})
        except Exception:
            r = el.rect
            d.execute_script("mobile: clickGesture", {"x": r["x"] + r["width"]//2,
                                                    "y": r["y"] + r["height"]//2})
        self.funciones.click_fab_plus()

    def cargar_datos_ocupacion_domicilio(self):
        # ocupacion
        self.funciones.validar_elemento_presente_xpath('//android.widget.ScrollView/android.widget.EditText[1]')
        self.funciones.escribir_por_xpath('//android.widget.ScrollView/android.widget.EditText[1]', 'taxista')
        self.funciones.clickear_por_xpath('//android.view.View[@content-desc="Gender"]')
        time.sleep(0.5)
        # domicilio - pais
        self.funciones.validar_elemento_presente_xpath('//android.widget.ScrollView/android.widget.ImageView[2]/android.view.View')
        self.funciones.clickear_por_xpath('//android.widget.ScrollView/android.widget.ImageView[2]/android.view.View')
        # >> buscar en paises
        self.funciones.escribir_por_xpath('//android.widget.EditText', 'argentina')
        time.sleep(0.5)
        self.funciones.clickear_por_xpath('//android.widget.ImageView[@content-desc="Argentina"]')
        # provincia
        self.funciones.validar_elemento_presente_xpath('//android.widget.ScrollView/android.widget.ImageView[2]/android.view.View')
        self.funciones.clickear_por_xpath('//android.widget.ScrollView/android.widget.ImageView[2]/android.view.View')
        # >> buscar en provincia
        self.funciones.escribir_por_xpath('//android.widget.EditText', 'Distrito')
        time.sleep(0.5)
        self.funciones.clickear_por_xpath('//android.widget.ImageView[@content-desc="Distrito federal (CABA)"]')
        time.sleep(0.5)
        # >>
        self.funciones.scroll_hasta_elemento('//android.widget.ScrollView/android.widget.EditText[2]', 1)
        self.funciones.escribir_por_xpath('//android.widget.ScrollView/android.widget.EditText[2]', 'Caballito')
        time.sleep(0.5)
        self.funciones.clickear_por_xpath('//android.view.View[@content-desc="Place of residence *"]')
        # >>> click en check box
        self.funciones.scroll_hasta_elemento('new UiSelector().className("android.widget.CheckBox")',1)
        self.funciones.clickear_por_xpath('//android.widget.CheckBox')
        # guardar
        time.sleep(0.5)
        self.funciones.validar_elemento_presente_xpath('//android.widget.Button[@content-desc="Save changes"]')
        self.funciones.clickear_por_xpath('//android.widget.Button[@content-desc="Save changes"]')
        time.sleep(0.5)
        self.funciones.validar_elemento_presente_xpath('//android.view.View[@content-desc="Medical record"]')
        self.funciones.clickear_por_xpath('//android.view.View[@content-desc="Medical record"]')
        time.sleep(0.5)

    # validando el cambio de estado de 2/5 a 3/5
    def verificar_estado_2_5_a_3_5(self):
        self.funciones.validar_elemento_presente_xpath('//android.widget.ImageView[@content-desc="60%, 3/5 Complete your profile Upload your first document"]', 'CAMBIO DE ESTADO 2/5 A 3/5')
        
    
    # completar perfil 3/5 a 4/5 #######################
    def entrear_completar_perfil3(self, timeout=3):
        """time.sleep(0.7)
        self.funciones.click_por_coordenadas(300, 450)"""
        d = self.driver
        wait = WebDriverWait(d, timeout)
        # 1) Robustez: evita el % y los \n usando descriptionContains + fallback por XPath.
        candidatos = [
            (AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().description("60%, 3/5 Complete your profile Upload your first document")'),
            (AppiumBy.XPATH,
            '//android.widget.ImageView[@content-desc="60%, 3/5 Complete your profile Upload your first document"]'),
            # Si el progreso cambió, matchea cualquier n/5 + el texto:
            (AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().descriptionMatches("(?s).*[1-5]/5.*Complete\\s+your\\s+profile.*Upload\\s+your\\s+first\\s+document.*")'),
        ]
        el = None
        for by, sel in candidatos:
            try:
                el = wait.until(lambda drv: drv.find_element(by, sel))
                break
            except Exception:
                pass

        if el is None:
            try:
                scroll = ('new UiScrollable(new UiSelector().scrollable(true))'
                        '.scrollIntoView(new UiSelector().descriptionContains("Complete your profile"))')
                el = d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, scroll)
            except Exception:
                # evidencia y corta
                try:
                    self.funciones.tomar_screenshot("no_element_completar_perfil")
                finally:
                    raise
        try:
            d.execute_script("mobile: clickGesture", {"elementId": el.id})
        except Exception:
            r = el.rect
            d.execute_script("mobile: clickGesture", {"x": r["x"] + r["width"]//2,
                                                    "y": r["y"] + r["height"]//2})
        self.funciones.click_fab_plus()

    def guardar_sin_completar_alerta_error(self):
        # validar mensaje de error por campos obligatorios
        self.funciones.clickear_por_xpath('//android.view.View[@content-desc="Scrim"]')
        self.funciones.clickear_por_xpath('//android.widget.Button[@content-desc="Upload file"]')
        self.funciones.validar_elemento_presente_xpath('//android.view.View[@content-desc="You must upload at least one file"]', 'VALIDAR MENSAJE DE ERROR POR CAMPOS OBLIGATORIOS')
        
    def cargar_primer_documento(self):
        # cargar documento
        self.funciones.click_por_coordenadas(950, 1840) #>> boton mas +
        time.sleep(1.5)
        self.funciones.click_por_coordenadas(200, 2100) #>> open files
        time.sleep(1.5)
        self.funciones.click_por_coordenadas(300, 1000) #>> seleccionar imagen
        time.sleep(0.5)
        self.funciones.validar_elemento_presente_xpath('//android.widget.ScrollView/android.view.View[6]/android.view.View/android.view.View/android.widget.ImageView[1]', 'documento cargado')
        # selecionado carpeta donde guardar el documento >>>
        self.funciones.clickear_por_xpath('//android.widget.ScrollView/android.widget.ImageView[1]/android.view.View')
        self.funciones.clickear_por_xpath('//android.widget.ImageView[@content-desc="Analytics (analysis)"]') 
        self.funciones.escribir_por_xpath('//android.widget.EditText', 'primer doc')
        # guardar
        self.funciones.validar_elemento_presente_xpath('//android.widget.Button[@content-desc="Upload file"]')
        self.funciones.clickear_por_xpath('//android.widget.Button[@content-desc="Upload file"]')        
        self.funciones.validar_elemento_presente_xpath('//android.view.View[@content-desc="Analytics (analysis)"]')
        self.funciones.clickear_por_xpath('//android.view.View[@content-desc="Analytics (analysis)"]')


        
    def verificar_estado_3_5_a_4_5(self):
        self.funciones.validar_elemento_presente_xpath('//android.widget.ImageView[@content-desc="80%, 4/5 Complete your profile Select your Interests"]', 'CAMBIO DE ESTADO 3/5 A 4/5')
        
        

    #completar perfil 4/5 a 5/5 #######################
    def entrar_completar_perfil4(self, timeout=3):
        """time.sleep(0.5)
        self.funciones.click_por_coordenadas(300, 450)"""
        d = self.driver
        wait = WebDriverWait(d, timeout)

        # Locators robustos (sin depender del % exacto ni de \n)
        candidatos = [
            # 1) Regex por UIAutomator: buscamos 4/5 + textos clave (tolerante a \n y espacios)
            (AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().descriptionMatches("(?s).*4/5.*Complete\\s+your\\s+profile.*Select\\s+your\\s+Interests.*")'),
            (AppiumBy.XPATH,
            '//*[@content-desc and '
            'contains(@content-desc,"4/5") and '
            'contains(@content-desc,"Complete your profile") and '
            'contains(@content-desc,"Select your Interests")]'),
        ]

        el = None
        for by, sel in candidatos:
            try:
                el = wait.until(lambda drv: drv.find_element(by, sel))
                break
            except Exception:
                pass

        if el is None:
            # Fallback: por si está fuera de vista dentro de un ScrollView
            try:
                scroll = ('new UiScrollable(new UiSelector().scrollable(true).instance(0))'
                        '.scrollIntoView(new UiSelector().descriptionContains("Select your Interests"))')
                el = d.find_element(AppiumBy.ANDROID_UIAUTOMATOR, scroll)
            except Exception:
                try:
                    self.funciones.tomar_screenshot("no_element_completar_perfil_4_5")
                finally:
                    raise

        # Tap por elementId y, si no, por coordenadas
        try:
            d.execute_script("mobile: clickGesture", {"elementId": el.id})
        except Exception:
            r = el.rect
            d.execute_script("mobile: clickGesture", {"x": r["x"] + r["width"]//2,
                                                    "y": r["y"] + r["height"]//2})
        self.funciones.click_fab_plus()
            

    def seleccionar_interes(self):
        self.funciones.validar_elemento_presente_xpath('//android.view.View[@content-desc="Pregnancy"]', 'seleccionar interes - pregnancy')
        self.funciones.clickear_por_xpath('//android.view.View[@content-desc="Pregnancy"]')
        self.funciones.clickear_por_xpath('//android.widget.Button[@content-desc="Save changes"]')

    def validar_interes_seleccionado_en_tips(self):
        self.funciones.validar_elemento_presente_uiautomator("new UiSelector().description('Pregnancy During pregnancy During pregnancy, it's crucial to maintain a balanced diet rich in vitamins and minerals. Don’t forget to consult your doctor about any supplements you might need for you and your baby, such as folic acid.')", "interes seleccionado en tips")
    
    def verificar_estado_4_5_a_5_5(self):
        self.funciones.clickear_por_xpath('//android.widget.ImageView[@content-desc="Home"]')
        self.funciones.validar_elemento_presente_xpath('//android.widget.ImageView[@content-desc="100%, 5/5 Complete your profile Invite more people to use Medicenter"]', 'CAMBIO DE ESTADO 4/5 A 5/5')
