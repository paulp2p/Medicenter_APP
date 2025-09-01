from behave import *
from pages.historia_clinica_page import *
from utils.funciones import *

# 006 y 007 features
@when(u'ingresar el usuario y la contraseña registrados')
def step_impl(context):
    context.historia_clinica_page.ingresar_usuario()
    context.historia_clinica_page.ingresar_clave()


@when(u'ingresar un usuario y contraseña validos') #008-features
def step_impl(context):
    context.historia_clinica_page.ingresar_usuario2()
    context.historia_clinica_page.ingresar_clave2()

@when(u'ingresar a ver mas folder de historia clinica') #006-feature
def step_impl(context):
    context.historia_clinica_page.vermas_my_chart()

@when(u'dar click en editar datos personales') #006-feature
def step_impl(context):
    context.historia_clinica_page.click_en_editar_datos_personales()

@when(u'completar datos personales') #006-feature
def step_impl(context):
    context.historia_clinica_page.editar_datos_personales()
    context.historia_clinica_page.borrar_datos_de_domicilio()

@when(u'agregar ocupacion')
def step_impl(context):
    context.historia_clinica_page.editar_datos_personales()

@when(u'editar ubicacion por ubicacion actual') #007-feature
def step_impl(context):
    context.historia_clinica_page.seleccionar_ubicacion()

@when(u'seleccionar pais') #006-feature
def step_impl(context):
    context.historia_clinica_page.seleccionar_pais_datos_personales()
   
@when(u'seleccionar cuidad y agregar direccion') #006-feature
def step_impl(context):
    context.historia_clinica_page.seleccionar_provincia_detos_personales()

@when(u'elimiar informacion de datos personales') #008-feature
def step_impl(context):
    context.historia_clinica_page.eliminar_datos_personales()

@when(u'eliminar toda la informacion de domicilio') #009-feature
def step_impl(context):
    context.historia_clinica_page.eliminar_info_de_domicilio()

@when(u'dar click en Edit personal data') #009-feature
def step_impl(context):
    context.historia_clinica_page.click_en_salir_editar_datos_personales()

@then(u'validar mensjaes de error en campos obligatorios') #009-feature
def step_impl(context):
    context.historia_clinica_page.validar_mensajes_de_campos_obligatorios()

@then(u'guardar datos personales') #006-feature
def step_impl(context):
    context.historia_clinica_page.guardar_datos_personales()

@then(u'valiar el popup de mensaje') #008-feature
def step_impl(context):
    context.historia_clinica_page.validar_popup()

@when(u'dar click en editar datos de salud') #010-feature
def step_impl(context):
    context.historia_clinica_page.click_en_editar_informacion_de_salud()

@when(u'editar datos de salud') #010-feature
def step_impl(context):
    context.historia_clinica_page.clickear_en_grupo_sanguinio()
    context.historia_clinica_page.input_alergia()

@then(u'guardar datos editados') #010-feature
def step_impl(context):
    context.historia_clinica_page.guardar_informacion_de_salud()

@then(u'salir de datos personales') #008-feature
def step_impl(context):
    context.historia_clinica_page.salir_de_editar_informacion()
   