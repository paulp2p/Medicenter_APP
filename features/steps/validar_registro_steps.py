from behave import *
from pages.registro_page import RegistroPage
from utils.funciones import *


@when(u'ingresar el usuario y la contraseña')
def step_impl(context):
    context.registro_page.presionar_sign_in()
    context.registro_page.ingresar_username_validar_perfil()
    
@when(u'clicar en header Complete your profile')
def step_impl(context):
    context.registro_page.entrar_en_completar_perfil()
    context.registro_page.select_region()
    context.registro_page.select_documento_de_identidad()

@when(u'cargar documentos de indentidad')
def step_impl(context):
    context.registro_page.subir_dni()
    # NO SE COMPLETA EL REGISTRO PORQUE PASA HACER MANUAL 
    # ASI COMO EL VIDEO SELFIE PARA VALIDAR EL REGISTRO