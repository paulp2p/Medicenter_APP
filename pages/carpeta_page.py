
from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.funciones import Funciones
from utils.val_locator import Localizadores as vl
import time

t = 1

class CarpetaPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)
        self.funciones = Funciones(driver)

    # --------  ------
    def click_en_btn_mas(self):#11  crear nueva carpeta
        self.funciones.validar_y_clickear_por_uiautomator(vl.BTN_MAS, 'click en el botón de más')
    
    def crear_nueva_carpeta(self):#11  crear nueva carpeta
        self.funciones.click_por_coordenadas(200, 1970)
        self.funciones.escribir_por_xpath(self, vl.NOMBRE_DE_CARPETA, "Test", 1)
        self.funciones.clickear_por_xpath(vl.BTN_CREAR_CARPETA, "creando nueva carpeta")
        self.funciones.scroll_hasta_elemento(vl.PATH_CARPETA_CREADA, 1)
        self.funciones.tomar_screenshot("carpeta creada")
        print(self.driver.page_source)

    def validar_carpeta_creada(self):#11  crear nueva carpeta
        self.funciones.scroll_hasta_elemento(vl.PATH_CARPETA_CREADA, 1)
        self.funciones.validar_elemento_presente_uiautomator(vl.PATH_CARPETA_CREADA,'carpeta creada correctamente')

    def buscar_carpeta_creada(self):#12 editar nombre de carpeta
        self.funciones.scroll_hasta_elemento(vl.PATH_CARPETA_CREADA, 1)
        #self.funciones.clickear_por_xpath('//android.view.View[@content-desc="Test 0 Items"]/android.widget.ImageView[2]')
        
    def cambiar_nombre_de_carpeta(self): #12 editar nombre de carpeta
        self.funciones.click_por_coordenadas(610, 1060) 
        time.sleep(0.5)
        self.funciones.click_por_coordenadas(200, 1730) 
        self.funciones.borrar_input('//android.widget.EditText[@text="Test"]')
        self.funciones.escribir_por_xpath(self,'//android.widget.EditText[@text="Test"]', "Test2")
        self.funciones.clickear_por_xpath(vl.CAMBIAR_NOMBRE)

    def validar_cambio_nombre(self): #12 editar nombre de carpeta
        self.funciones.scroll_hasta_elemento(vl.CARPETA_RENOMBRADA, 1)
        self.funciones.validar_elemento_presente_uiautomator("Test2 0 Items")

    def eliminar_carpeta(self):#14
        self.funciones.scroll_hasta_elemento(vl.CARPETA_RENOMBRADA, 1)
        self.funciones.click_por_coordenadas(610, 1060) 
        time.sleep(0.5)
        self.funciones.click_por_coordenadas(200, 2080)
        self.funciones.clickear_por_xpath('//android.widget.Button[@content-desc="Delete"]', "eliminando carpeta")
        self.funciones.tomar_screenshot("carpeta eliminada")

    def crear_carpera_sin_nombre(self):#15 carpeta sin nombre
        self.funciones.validar_y_clickear_por_uiautomator(vl.BTN_MAS, 'click en el botón de más')
        self.funciones.click_por_coordenadas(200, 1970)
        self.funciones.clickear_por_xpath(vl.BTN_CREAR_CARPETA, "creando nueva carpeta")
        self.funciones.capturar_imagen_por_uiautomator(vl.ERROR_CARPETA_SIN_NOMBRE, 'error al crear carpeta sin nombre')

    def cancelar_crear_carpeta(self):#15  
        self.funciones.click_por_coordenadas(200, 1970)
        self.funciones.capturar_imagen_por_uiautomator('new UiSelector().description("New folder")', 'cancelar crear carpeta')
        self.funciones.clickear_por_uiautomator('new UiSelector().description("Cancel")')

