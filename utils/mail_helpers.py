import os
from utils.mailtm_client import MailTmClient

def obtener_codigo_de_mail_guardado(timeout=60):
    ruta = "datos_generados/temp_email.txt"
    if not os.path.exists(ruta):
        raise FileNotFoundError("[ERROR] No se encontró el archivo con el email temporal.")

    with open(ruta, "r", encoding="utf-8") as f:
        email = f.read().strip()

    # Crear cliente de mail nuevo y autenticarse con el email guardado
    mail_client = MailTmClient()
    mail_client.address = email
    mail_client.authenticate()

    print("[INFO] Esperando nuevo código de verificación para el email guardado...")
    mensaje = mail_client.wait_for_email(timeout=timeout)
    print(f"[INFO] Email recibido: {mensaje.get('subject')}")

    texto = mail_client.get_message_text(mensaje["id"])
    print(f"[DEBUG] Contenido del mensaje:\n{texto}")

    codigo = mail_client.extract_code_from_message(texto)
    if codigo:
        print(f"[INFO] Código de verificación extraído: {codigo}")
        return codigo
    else:
        raise Exception("[ERROR] No se encontró un código de verificación.")
