from behave import *
from pages.cuenta_page import CuentaPage
import os
from utils.otp_helper import attach_otp_to_allure
"""
NUMERO_LOCAL_SIN_54 = "".join(ch for ch in os.getenv("STAGING_PHONE_LOCAL", "91100000001") if ch.isdigit())
AUTO_SEND = os.getenv("AUTO_SEND_TO_MOCK", "0") == "1"   # 1 = activar simulación
FIXED_OTP = os.getenv("STAGING_FIXED_OTP", "1234")       # OTP fijo cuando simulamos
"""
@when(u'presionar boton cuenta')
def step_impl(context):
    context.cuenta_page.click_boton_cuenta()

@when(u'editar username')
def step_impl(context):
    context.cuenta_page.editar_username_de_informacion_de_cuenta()

@then(u'validar que se cambion el username')
def step_impl(context):
    context.cuenta_page.validar_userneme()
    context.cuenta_page.volver_al_username_original()

#----------------------------------------------------------------------
@when(u'editar email')
def step_impl(context):
    context.cuenta_page.editar_email_en_informacion_de_cuenta()

@then(u'validar si se produjo el cambio de email')
def step_impl(context):
    context.cuenta_page.validar_cambio_email()

#----------------------------------------------------------------------
@when(u'cambiar imagen de perfil seleccionar de la galeria')
def step_impl(context):
    context.cuenta_page.opciones_de_foto_perfil()

@then(u'validar cambio de imagen de perfil')
def step_impl(context):
    context.cuenta_page.validar_cambio_de_nueva_imagen_de_perfil()

#----------------------------------------------------------------------
@when(u'eliminar imagen de perfil')
def step_impl(context):
    context.cuenta_page.eliminar_imagen_de_perfil()

@then(u'screen shot de imagen de perfil')
def step_impl(context):
    context.cuenta_page.screen_shot_imagen_de_perfil()

#----------------------------------------------------------------------
@when(u'borrar campos de username y email')
def step_impl(context):
    context.cuenta_page.campos_obligatorios()

@then(u'validar mensaje alerta de campos obligatorios')
def step_impl(context):
    context.cuenta_page.validar_mensaje_alerta_de_campos_obligatorios()

#----------------------------------------------------------------------
@when(u'guardar sin completat datos de obra social')
def step_impl(context):
    context.cuenta_page.campos_obligatorios()

@then(u'validar mensaje de error de campos obligatorios')
def step_impl(context):
    context.cuenta_page.validar_mensaje_alerta_de_campos_obligatorios()

#----------------------------------------------------------------------
@when(u'cambiar nro de telefono')
def step_cambiar_nro(context):
    # Limpio el mock antes (por las dudas)
   """ try:
        context.mock_sms.flush(f"+54{NUMERO_LOCAL_SIN_54}")
        if NUMERO_LOCAL_SIN_54.startswith("9"):
            context.mock_sms.flush(f"+54{NUMERO_LOCAL_SIN_54[1:]}")
    except Exception:
        pass

    context.cuenta_page.cambiar_nro_telefono(
        numero_local=NUMERO_LOCAL_SIN_54,
        mock_sms=context.mock_sms,
        hacer_flush=False
    )

    # Si el backend aún no envía al mock, simulamos
    if AUTO_SEND:
        tos = [f"+54{NUMERO_LOCAL_SIN_54}"]
        if NUMERO_LOCAL_SIN_54.startswith("9"):
            tos.append(f"+54{NUMERO_LOCAL_SIN_54[1:]}")

        for to in tos:
            try:
                context.mock_sms.send(to, f"Tu código es {FIXED_OTP}", "test")
            except Exception:
                pass"""


@then(u'validar codigo de verificacion de cambio de nro de telefono')
def step_validar_codigo(context):
    """from utils.otp_helper import attach_otp_to_allure
    auto = os.getenv("AUTO_SEND_TO_MOCK", "1").lower() in ("1","true","yes","on")
    timeout = 30 if auto else 180

    otp, to_usado, raw = context.cuenta_page.esperar_y_ingresar_otp_4(
        context.mock_sms, timeout=timeout, poll=2
    )
    attach_otp_to_allure(otp, name="OTP verificación (mask)")

    try:
        import allure, json
        allure.attach(to_usado or "N/A", name="MockSMS to usado", attachment_type=allure.attachment_type.TEXT)
        allure.attach(json.dumps(raw, ensure_ascii=False, indent=2), name="MockSMS last (raw)", attachment_type=allure.attachment_type.JSON)
    except Exception:
        pass"""



