from dotenv import dotenv_values
import os

def load_config(env_name="staging"):
    env_path = os.path.join(os.path.dirname(__file__), "environments", f"{env_name}.env")
    return dotenv_values(env_path)
