# services/mock_sms_client.py
import time
import requests
import re
from typing import List, Tuple, Optional

class MockSMSClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8081"):
        self.base_url = base_url.rstrip("/")

    def health(self) -> dict:
        r = requests.get(f"{self.base_url}/health", timeout=10)
        r.raise_for_status()
        return r.json()

    def send(self, to: str, text: str, sender: str | None = "staging") -> dict:
        r = requests.post(f"{self.base_url}/send", json={"to": to, "text": text, "sender": sender}, timeout=10)
        r.raise_for_status()
        return r.json()

    def last(self, to: str) -> dict:
        r = requests.get(f"{self.base_url}/last", params={"to": to}, timeout=10)
        r.raise_for_status()
        return r.json()

    def flush(self, to: str | None = None) -> dict:
        url = f"{self.base_url}/flush" + (f"?to={to}" if to else "")
        r = requests.post(url, timeout=10)
        r.raise_for_status()
        return r.json()

    def wait_otp(self, to: str, timeout: int = 180, poll: int = 3, otp_len: int = 4) -> Optional[str]:
        fin = time.time() + timeout
        pat = re.compile(rf"\b(\d{{{otp_len}}})\b")
        while time.time() < fin:
            try:
                data = self.last(to)
                if data.get("ok"):
                    text = data.get("text") or ""
                    m = pat.search(text)
                    if m:
                        return m.group(1)
            except Exception:
                pass
            time.sleep(poll)
        return None

    def wait_otp_candidates(
        self,
        tos: List[str],
        timeout: int = 180,
        poll: int = 3,
        otp_len: int = 4
    ) -> Tuple[Optional[str], Optional[str], Optional[dict]]:
        fin = time.time() + timeout
        pat = re.compile(rf"\b(\d{{{otp_len}}})\b")
        while time.time() < fin:
            for to in tos:
                try:
                    data = self.last(to)
                    if data.get("ok"):
                        text = data.get("text") or ""
                        m = pat.search(text)
                        if m:
                            return m.group(1), to, data
                except Exception:
                    pass
            time.sleep(poll)
        return None, None, None
