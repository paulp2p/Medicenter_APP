from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.funciones import Funciones
from utils.val_locator import Localizadores as vl
from utils.mailtm_client import MailTmClient
from utils.mail_helpers import obtener_codigo_de_mail_guardado
from faker import Faker
import random

import os
import time

t = 3

class Historia_clinica:
    def __init__(self, driver, mail_client):
        self.driver = driver
        self.wait = WebDriverWait(driver, 60)
        self.funciones = Funciones(driver)
        self.mail_client = mail_client
        self.faker = Faker('es_ES')
        # lista de ocupaciones
        self.ocupaciones = [
            "QA Engineer", "Médico", "Abogado", "Profesor",
            "Ingeniero", "Analista",
            "Enfermero", "Arquitecto"
        ]
        # lista de direcciones
        self.direcciones = [
            "Siempre Viva 742", "Falsa 123",
            "San Martín 450", "Belgrano 789", 
            "Mitre 1200", "Rivadavia 233", 
            "Corrientes 1520", "Lavalle 890"
        ]
        # lista de alergias
        self.alergias = [
            "cafeína", "leche",
            "carne", "fruta",
            "pescado", "queso"
        ]
       
    
    def obtener_username_guardado(self):
        ruta = "datos_generados/username.txt"
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read().strip()
        
    def ingresar_usuario(self):
        self.funciones.escribir_por_uiautomator(vl.CAMPO_USER, "danielruiz")

    def ingresar_clave(self):
        self.funciones.escribir_por_uiautomator(vl.CAMPO_PASSW, "Test12345")

    def ingresar_usuario2(self):
        self.funciones.escribir_por_uiautomator(vl.CAMPO_USER, "danielruiz")

    def ingresar_clave2(self):
        self.funciones.escribir_por_uiautomator(vl.CAMPO_PASSW, "Test12345")

    def vermas_my_chart(self):
        self.funciones.clickear_por_uiautomator(vl.BTN_VER_MAS,"boton ver mas - carpeta de historia clinica")
        self.funciones.validar_elemento_presente_uiautomator('new UiSelector().description("Medical record")')
    
    def click_en_editar_datos_personales(self):
        self.funciones.clickear_por_uiautomator(vl.BTN_EDITAR_DATOS_PERSONALES, "boton editar datos personales")

    def ocupacion_random(self):
        return random.choice(self.ocupaciones)

    def editar_datos_personales(self):
        self.funciones.borrar_input_total(vl.INPUT_OCUPACION)#*
        ocupacion = self.ocupacion_random()
        self.funciones.escribir_por_uiautomator(vl.BUSCADOR, ocupacion)
        self.funciones.clickear_por_uiautomator('new UiSelector().description("Gender")')

    def borrar_datos_de_domicilio(self):
        self.funciones.clickear_por_uiautomator(vl.DELETE_COUNTRY_POPUP)
        self.funciones.clickear_por_uiautomator(vl.DELETE_OTHER_COUNTRY)
        self.funciones.borrar_input_total(vl.DELETE_ADDRESS)#*
        time.sleep(1)
        self.funciones.borrar_input_total(vl.DELETE_ADDRESS)#*
        self.funciones.clickear_por_uiautomator('new UiSelector().description("Place of birth *")')
        

    def seleccionar_ubicacion(self):
        self.funciones.clickear_por_uiautomator(vl.DELETE_COUNTRY_POPUP)
        self.funciones.clickear_por_uiautomator(vl.UBICACION_ACTUAL)
        self.funciones.clickear_por_uiautomator(vl.CLICK_EN_PANTALLA, "GUARDANDO DIRECCION NUEVA")
        self.funciones.scroll_hasta_elemento(vl.CHECK_BOX_RESIDENCE)
        self.funciones.clickear_por_uiautomator(vl.CHECK_BOX_RESIDENCE)

    def seleccionar_pais_datos_personales(self):
        #self.funciones.clickear_por_uiautomator(vl.DELETE_COUNTRY_POPUP)
        self.funciones.clickear_por_uiautomator(vl.INPUT_COUNTRY)
        self.funciones.escribir_por_uiautomator(vl.BUSCADOR, "argentina")
        self.funciones.clickear_por_uiautomator(vl.SELECT_PAIS)

    def direccion_random(self):
        return random.choice(self.direcciones)

    def seleccionar_provincia_detos_personales(self): #006-feature
        self.funciones.clickear_por_uiautomator(vl.INPUT_PROVINCE)
        self.funciones.escribir_por_uiautomator(vl.BUSCADOR, "Distrito Federal (CABA)")
        self.funciones.clickear_por_uiautomator(vl.SELECT_PROVINCE)
        direccion = self.direccion_random()
        self.funciones.escribir_por_uiautomator(vl.INPUT_DOMICILIO, direccion)
        self.funciones.clickear_por_uiautomator(vl.CLICK_EN_PANTALLA, "GUARDANDO DIRECCION NUEVA")
        self.funciones.clickear_por_uiautomator(vl.CHECK_BOX_RESIDENCE)

    def eliminar_datos_personales(self):
        self.funciones.clickear_por_uiautomator(vl.DELETE_COUNTRY_POPUP)
        self.funciones.scroll_hasta_elemento(vl.DELETE_OTHER_COUNTRY)
        self.funciones.clickear_por_uiautomator(vl.DELETE_OTHER_COUNTRY)

    def eliminar_info_de_domicilio(self): #9
        self.funciones.clickear_por_uiautomator(vl.DELETE_COUNTRY_POPUP)
        self.funciones.scroll_hasta_elemento(vl.DELETE_OTHER_COUNTRY)
        self.funciones.clickear_por_uiautomator(vl.DELETE_OTHER_COUNTRY)

    def click_en_salir_editar_datos_personales(self): #9
        self.funciones.clickear_por_uiautomator(vl.LINK_EDIT_PERSONAL_DATA, "BOTON EDIT PERSONAL DATA")
    
    def validar_mensajes_de_campos_obligatorios(self): #9
        self.funciones.validar_elemento_presente_uiautomator(vl.MSJ_CAMPO_OBLIGATORIO1, "mensaje de campos obligatorios 1")
        self.funciones.validar_elemento_presente_uiautomator(vl.MSJ_CAMPO_OBLIGATORIO2, "mensaje de campos obligatorios 2")

    def guardar_datos_personales(self):
        self.funciones.tomar_screenshot("guardar datos personales")
        self.funciones.clickear_por_uiautomator(vl.BTN_SAVE, "boton guardar")

    def validar_popup(self):
        self.funciones.validar_elemento_presente_uiautomator(vl.POPUP_MJS, "buttom sheet: perderas los cambios")

    def click_en_editar_informacion_de_salud(self): #10 
        self.funciones.clickear_por_uiautomator(vl.BTN_EDITAR_INFORMACION_DESALUD)

    def clickear_en_grupo_sanguinio(self): #10
        self.funciones.validar_elemento_presente_uiautomator(vl.BG_A, 'opciones de grupo sanguinio visible')
        opciones = ["O", "A", "B", "AB"]  # si realmente tenés "B" repetido, corregilo a "AB"
        self.funciones.click_random_uia_por_description(
            opciones,
            persist_key="grupo_sanguineo",
            persist_path="datos_generados/random_choices.json",
            avoid_repeat=True,     # no repetir la última entre corridas
            avoid_checked=True,    # no tocar la ya marcada
            timeout_probe=3,
            timeout_click=10
        )
        #self.funciones.click_random(vl.BG_A, vl.BG_C, tipo='uiautomator', descripcion='elegir grupo sanguinio')
        self.funciones.click_random(vl.BF_POSITIVO, vl.BF_NEGATIVO, tipo='uiautomator', descripcion='factor sanguinio')
        self.funciones.click_random(vl.ALCOHOL_S, vl.ALCOHOL_N, tipo='xpath' , descripcion='elegir alcoholismo')
        self.funciones.click_random(vl.FUMAR_S, vl.FUMSR_N, tipo='xpath', descripcion='fumador')
        self.funciones.click_random(vl.DRUG_S, vl.DRUG_N, tipo='xpath', descripcion='adiccion a drogas')

    def alergia_random(self):
        return random.choice(self.alergias)
    
    def input_alergia(self): #10
        alergia = self.alergia_random()
        self.funciones.scroll_hasta_elemento('new UiSelector().description("Allergy 1")', 1)
        self.funciones.clickear_por_uiautomator(vl.ELIMINAR_ALERGIA)
        self.funciones.escribir_por_uiautomator(vl.ESCRIBIR_ALERGIA, alergia)
    
    def guardar_informacion_de_salud(self): #10
        self.funciones.validar_y_clickear_por_uiautomator(vl.BTN_GUARDAR_INF_SALUD, "guardar informacion de salud")
        
    def salir_de_editar_informacion(self): #08
        self.funciones.clickear_por_uiautomator(vl.LINK_EDIT_PERSONAL_DATA, "popup mensaje perderas los cambios realizados")
    
    
    
        