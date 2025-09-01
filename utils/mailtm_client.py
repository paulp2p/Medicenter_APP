import os
import time
import requests
from typing import Optional

class MailTmClient:
    def __init__(self, timeout: int = 60, base_url: str = "https://api.mail.tm",
                 auto_create: bool = True, password: Optional[str] = None, session: Optional[requests.Session] = None):
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.timeout = timeout
        self.password = password or "12345"
        self.token: Optional[str] = None
        self.address: Optional[str] = None
        self.account_id: Optional[str] = None
        if auto_create:
            self.ensure_account_ready()

    def set_timeout(self, timeout: int):
        self.timeout = int(timeout)

    def ensure_account_ready(self):
        if not self.address:
            self.create_account()

    def create_account(self):
        resp = self.session.get(f"{self.base_url}/domains", timeout=self.timeout)
        resp.raise_for_status()
        domains = resp.json().get("hydra:member", [])
        if not domains:
            raise RuntimeError("Mail.tm: no hay dominios disponibles.")
        domain = domains[0]["domain"]

        self.address = f"test{int(time.time())}@{domain}"
        payload = {"address": self.address, "password": self.password}
        resp = self.session.post(f"{self.base_url}/accounts", json=payload, timeout=self.timeout)
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Error creando cuenta: {resp.status_code} - {resp.text}")

        self.account_id = resp.json().get("id")
        ruta = "datos_generados/temp_email.txt"
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(self.address)

        self.authenticate()

    def authenticate(self):
        if not self.address:
            raise RuntimeError("No hay address configurado. Llama a create_account() primero.")
        payload = {"address": self.address, "password": self.password}
        resp = self.session.post(f"{self.base_url}/token", json=payload, timeout=self.timeout)
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Error autenticando: {resp.status_code} - {resp.text}")
        self.token = resp.json().get("token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def wait_for_email(self, subject_filter: Optional[str] = None,
                       timeout: Optional[int] = None,
                       retry_if_fail: bool = True,
                       poll_interval: int = 3):
        self.ensure_account_ready()
        deadline = time.time() + (timeout or self.timeout)

        def _poll(until_ts):
            while time.time() < until_ts:
                try:
                    resp = self.session.get(f"{self.base_url}/messages", timeout=self.timeout)
                    if resp.status_code != 200:
                        time.sleep(poll_interval)
                        continue
                    data = resp.json()
                    messages = data.get("hydra:member", [])
                    for msg in messages:
                        subj = (msg.get("subject") or "").lower()
                        if subject_filter is None or subject_filter.lower() in subj:
                            return msg
                except Exception:
                    pass
                time.sleep(poll_interval)
            return None

        msg = _poll(deadline)
        if msg:
            return msg

        if retry_if_fail:
            self.create_account()
            msg = _poll(time.time() + 30)
            if msg:
                return msg

        raise TimeoutError("No se recibió ningún email válido en el tiempo establecido.")

    def get_message_text(self, message_id: str) -> str:
        resp = self.session.get(f"{self.base_url}/messages/{message_id}", timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        text = data.get("text")
        if not text:
            text = data.get("intro") or ""
        return text

    @staticmethod
    def extract_code_from_message(text: str) -> Optional[str]:
        import re
        m = re.search(r"\b\d{4,6}\b", text)
        return m.group(0) if m else None

    def login(self):
        self.authenticate()
