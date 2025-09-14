
import time, math
from orionmentor.core.telemetry.store import STORE

def estimate_tokens(txt: str) -> int:
    return max(1, math.ceil(len(txt)/4))

def timed_call(fn, *args, **kwargs):
    t0 = time.perf_counter()
    out = fn(*args, **kwargs)
    dt = (time.perf_counter() - t0) * 1000.0
    return out, dt

def log_event(stage: str, req_id: str | None = None, **fields):
    msg = " ".join(f"{k}={v}" for k,v in fields.items())
    print(f"[telemetry] {stage} :: {msg}")
    STORE.record(stage=stage, req_id=req_id or "-", **fields)
