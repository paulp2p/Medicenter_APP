from dotenv import dotenv_values
import os

def load_config(env_name="staging"):
    """
    Carga el .env del entorno y permite override por variables de entorno del sistema.
    """
    base_dir = os.path.dirname(__file__)
    env_path = os.path.join(base_dir, "environments", f"{env_name}.env")

    file_cfg = dotenv_values(env_path)
    # Normaliza claves a str (dotenv puede retornar None)
    file_cfg = {k: v for k, v in file_cfg.items() if v is not None}

    # Permite overrides por variables del sistema (CI/CD, local, etc.)
    merged = {**file_cfg}
    for k in list(file_cfg.keys()):
        if k in os.environ and os.environ[k]:
            merged[k] = os.environ[k]

    # Expande rutas como ~ o %USERPROFILE% si viene APP
    if "APP" in merged and merged["APP"]:
        merged["APP"] = os.path.expandvars(os.path.expanduser(merged["APP"]))

    return merged
