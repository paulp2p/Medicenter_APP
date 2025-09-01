from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import re

app = FastAPI()
STORE = {}  # keys: variantes normalizadas del "to" -> {"text": str, "sender": str|None, "time": str, "to_orig": str}

class SMS(BaseModel):
    to: str
    text: str
    sender: str | None = None

def _digits(s: str) -> str:
    return "".join(ch for ch in s if ch.isdigit())

def _norm_variants(to_raw: str):
    ds = _digits(to_raw)
    if ds.startswith("00"):
        ds = ds[2:]
    if not ds.startswith("54"):
        return {f"+{ds}", ds}

    variants = set()
    base_plus = f"+{ds}"
    variants.add(base_plus)
    variants.add(ds)

    if len(ds) >= 3 and ds[0:2] == "54":
        if ds[2] == "9":
            sin9 = "+54" + ds[3:]
            variants.add(sin9)
            variants.add(sin9[1:])
        else:
            con9 = "+549" + ds[2:]
            variants.add(con9)
            variants.add(con9[1:])
    return variants

@app.get("/health")
def health():
    return {"ok": True, "service": "mock-sms"}

@app.post("/send")
def send_sms(sms: SMS):
    variants = _norm_variants(sms.to)
    rec = {"text": sms.text, "sender": sms.sender, "time": datetime.utcnow().isoformat(), "to_orig": sms.to}
    for key in variants:
        STORE[key] = rec
    print(f"[MOCK] /send to_orig={sms.to} -> keys={list(variants)} text={sms.text}")
    return {"ok": True, "stored_keys": list(variants)}

@app.get("/last")
def last_sms(to: str):
    for key in _norm_variants(to):
        rec = STORE.get(key)
        if rec:
            m = re.search(r"\b(\d{4})\b", rec["text"] or "")
            return {"ok": True, "otp": (m.group(1) if m else None), "key": key, **rec}
    return {"ok": False, "reason": "no_sms"}

@app.post("/flush")
def flush(to: str | None = None):
    if to:
        for key in _norm_variants(to):
            STORE.pop(key, None)
    else:
        STORE.clear()
    return {"ok": True}

@app.get("/dump")
def dump():
    return {"ok": True, "size": len(STORE), "items": STORE}
