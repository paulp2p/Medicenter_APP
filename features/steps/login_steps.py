from behave import *
from pages.login_page import LoginPage



@when(u'deslizar info de intro')
def step_impl(context):
    context.login_page.validar_pantalla_de_inicio()

@then(u'presionar boton sing in')
def step_impl(context):
    context.login_page.presionar_sign_in()
    context.login_page.validar_ingreso_a_pantalla_login()

@when('ingreso el usuario "{usuario}" y la contraseña "{clave}"')
def step_impl(context, usuario, clave):
    if not usuario:
        print(" Test recibió usuario vacío.")
    if not clave:
        print(" Test recibió clave vacía.")
    context.login_page.ingresar_usuario(usuario)
    context.login_page.ingresar_clave(clave)

@when("presionar boton ingresar")#003
def step_impl(context):
    context.login_page.presionar_btn_login()

@then("debería ver la pantalla principal")
def step_impl(context):
    context.login_page.valida_ingreso()
    context.login_page.cerrar_sesion()

@then("mensaje de error por usuario inválido")
def step_impl(context):
    context.login_page.usuario_invalido()

@then("mensaje de error por contraseña incorrecta")
def step_impl(context):
    context.login_page.clave_invalido()

@then(u'borrar las credenciales ingresadas')
def step_impl(context):
    context.login_page.borrar_credenciales()

@when("Visualizar Steps en el header")
def step_impl(context):
    context.login_page.validar_header()

@then(u'Cerrar sesion')
def step_impl(context):
    context.login_page.cerrar_sesion()

@when(u'Cerrar sesion')#003
def step_impl(context):
    context.login_page.cerrar_sesion()

@then(u'Iniciar sesion desde el centro de cuentas')
def step_impl(context):
    context.login_page.login_desde_centro_de_cuentas()

@then(u'Iniciar sesion con otra cuenta')
def step_impl(context):
    context.login_page.iniciar_sesion_con_otra_cuenta()

@then(u'cerrar app')
def step_impl(context):
    context.login_page.cerrar_apk()