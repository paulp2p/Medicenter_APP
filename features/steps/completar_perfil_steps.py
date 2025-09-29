from behave import *
from pages.completar_perfil_page import Completar_perfil


@when(u'eliminar cuenta de usuario')
def step_impl(context):
    context.completar_perfil_page.entrar_a_cuenta()
    context.completar_perfil_page.eliminar_cuenta()

@when(u'presionar boton go to home')
def step_impl(context):
    context.completar_perfil_page.go_to_home()

@when(u'entrar a completar perfil 2')
def step_impl(context):
    context.completar_perfil_page.entrar_a_completar_perfil2()


@when(u'completar datos de ocupacion y domicilio')
def step_impl(context):
    context.completar_perfil_page.cargar_datos_ocupacion_domicilio()

@then(u'verificar que el estado cambio de 2 a 3')
def step_impl(context):
    context.completar_perfil_page.verificar_estado_2_5_a_3_5()


@when(u'entrar a completar perfil 3')
def step_impl(context):
    context.completar_perfil_page.entrear_completar_perfil3()


@when(u'guardar sin completar - alerta mensaje de error')
def step_impl(context):
    context.completar_perfil_page.guardar_sin_completar_alerta_error()
    

@when(u'cargar el primer documento')
def step_impl(context):
    context.completar_perfil_page.cargar_primer_documento()


@then(u'verificar que el estado cambio de 3 a 4')
def step_impl(context):
    context.completar_perfil_page.verificar_estado_3_5_a_4_5()


@when(u'entrar a completar perfil 4')
def step_impl(context):
    context.completar_perfil_page.entrar_completar_perfil4()


@when(u'seleccionar un interes')
def step_impl(context):
    context.completar_perfil_page.seleccionar_interes()

@when(u'validar interes seleccionado en tips')
def step_impl(context):
    context.completar_perfil_page.validar_interes_seleccionado_en_tips()

@then(u'verificar que el estado cambio de 4 a 5')
def step_impl(context):
    context.completar_perfil_page.verificar_estado_4_5_a_5_5()