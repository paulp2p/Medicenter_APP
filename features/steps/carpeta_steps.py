from behave import *
from pages.carpeta_page import CarpetaPage


@when(u'presionar boton MAS') #12  crear nueva carpeta
def step_impl(context):
    context.carpeta_page.click_en_btn_mas()

@when(u'crear una carpeta') #12  crear nueva carpeta
def step_impl(context):
    context.carpeta_page.crear_nueva_carpeta()

@then(u'validar creacion de la carpeta') #12  crear nueva carpeta
def step_impl(context):
    context.carpeta_page.validar_carpeta_creada()
    
@when(u'buscar carpeta creada')#13 editar nombre de carpeta
def step_impl(context):
    context.carpeta_page.buscar_carpeta_creada()
    
@when(u'cambiar nombre de la carpeta')#13 editar nombre de carpeta
def step_impl(context):
    context.carpeta_page.cambiar_nombre_de_carpeta()
    
@then(u'validar que se cambio el nombre de la carpeta')#13 editar nombre de carpeta
def step_impl(context):
    context.carpeta_page.validar_cambio_nombre()
    
@then(u'eliminar carpeta')#13 eliminar carpeta 
def step_impl(context):
    context.carpeta_page.eliminar_carpeta()

@then(u'crear carpeta sin nombre')#15 eliminar carpeta  click en boton cancelar
def step_impl(context):
    context.carpeta_page.crear_carpera_sin_nombre()

@then(u'click en boton cancelar')#15 eliminar carpeta  - cancelar carpeta
def step_impl(context):
    context.carpeta_page.cancelar_crear_carpeta()