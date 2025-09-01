from behave import *
from pages.registro_page import RegistroPage
from utils.funciones import *

@when("Ingresar a crear cuenta y validar pantalla de campos input")
def step_impl(context):
    context.registro_page.ingresar_create_account()

@when("ingresar email - username - password - confirmar password")
def step_impl(context):
    context.registro_page.ingresar_datos()

@when("clicar en checkbox y btn Next")
def step_impl(context):
    context.registro_page.check_y_next()

@then("obtener y validar el código de verificación")
def step_impl(context):
    codigo = context.registro_page.obtener_codigo_verificacion()
    print(f"[INFO] Código recibido: {codigo}")
    context.codigo_verificacion = codigo

@when(u'clicar Reenviar código')
def step_impl(context):
    context.registro_page.reenviar_codigo()
    codigo = context.registro_page.obtener_codigo_verificacion()
    print(f"[INFO] Código recibido: {codigo}")
    context.codigo_verificacion = codigo

#---------------------------------------------------------------------------------

@when(u'ingresar código de verificación recibido')
def step_impl(context):
    context.registro_page.ingresar_codigo_verificacion(context.codigo_verificacion)


@then("validar pantalla de confirmacion de registro")
def step_impl(context):
    context.registro_page.validar_ingreso_registro()

@then("valida que paso el codigo de verificacion")
def step_impl(context):
    context.registro_page.validar_codigo_verificacion()

#---------------------------------------------------------------------------------

@when(u'ingresar email - validar los campos obligatorios faltantes')
def step_impl(context):
    context.registro_page.ingresar_email()
    context.registro_page.click_btn_next()
    context.registro_page.click_btn_back()


@when(u'ingresar username - validar los campos obligatorios faltantes')
def step_impl(context):
    context.registro_page.volver_a_crear_cuenta()
    context.registro_page.ingresar_username()
    context.registro_page.click_btn_next()
    context.registro_page.click_btn_back()

@when(u'ingresar password - validar los campos obligatorios faltantes')
def step_impl(context):
    context.registro_page.volver_a_crear_cuenta()
    context.registro_page.ingresar_password()
    context.registro_page.click_btn_next()
    context.registro_page.click_btn_back()
    #-----------------------------------
    context.registro_page.volver_a_crear_cuenta()
    context.registro_page.ingresar_password_confirmar()
    context.registro_page.click_btn_next()
    context.registro_page.click_btn_back()

@when(u'ingresar checkbox - validar los campos obligatorios faltantes')
def step_impl(context):
    context.registro_page.volver_a_crear_cuenta()
    context.registro_page.click_chack_box()
    context.registro_page.click_btn_next()
    context.registro_page.click_btn_back()

@then(u'obtener y validar el mensaje de error al clicar en btn Next')
def step_impl(context):
    context.registro_page.volver_a_crear_cuenta()
    context.registro_page.click_btn_next2()

#---------------------------------------------------------------------------------

@then(u'validar alerta mensajes de campos obligatorios')
def step_impl(context):
    context.registro_page.validar_alerta_de_campos_obligatorios()

#---------------------------------------------------------------------------------

@when(u'ingresar email invalido')
def step_impl(context):
    context.registro_page.escribir_mail_invalido()

@then(u'ferificar mensaje de mail invalido')
def step_impl(context):
    context.registro_page.verificar_mensaje_mail_invalido()
    
@when(u'reingresar a sección de crear cuenta')
def step_impl(context):
    context.registro_page.reingresar_a_seccion_crear_cuenta()
    
@when(u'ingresar contraseña invalida')
def step_impl(context):
    context.registro_page.ingresar_clave_invalida()

@then(u'verificar mensaje de contraseña invalida')
def step_impl(context):
    context.registro_page.verificar_mensaje_clave_invalida()