from __future__ import annotations
from collections import deque
from dataclasses import dataclass, asdict
from threading import Lock
from time import time
from typing import Deque, Dict, Any, List, Tuple
import csv, io

@dataclass
class Event:
    ts: float
    req_id: str
    stage: str          # route | prompt | llm | parse | validate
    fields: Dict[str, Any]

class TelemetryStore:
    def __init__(self, max_events: int = 5000):
        self._buf: Deque[Event] = deque(maxlen=max_events)
        self._lock = Lock()

    def record(self, stage: str, req_id: str, **fields):
        ev = Event(ts=time(), req_id=req_id, stage=stage, fields=fields)
        with self._lock:
            self._buf.append(ev)

    def recent(self, n: int = 200) -> List[Event]:
        with self._lock:
            return list(self._buf)[-n:]

    # ---------- Aggregazioni per dashboard ----------
    def summary(self) -> Dict[str, Any]:
        data = self.recent(2000)
        routed_small = sum(1 for e in data if e.stage == "route" and e.fields.get("target") == "small")
        routed_big   = sum(1 for e in data if e.stage == "route" and e.fields.get("target") == "big")
        served_small = sum(1 for e in data if e.stage == "llm" and e.fields.get("tier") == "small")
        served_big   = sum(1 for e in data if e.stage == "llm" and e.fields.get("tier") == "big")
        val_ok       = sum(1 for e in data if e.stage == "validate" and e.fields.get("ok") is True)
        val_fail     = sum(1 for e in data if e.stage == "validate" and e.fields.get("ok") is False)

        return {
            "routed": {"small": routed_small, "big": routed_big},
            "served": {"small": served_small, "big": served_big},
            "validation": {"ok": val_ok, "fail": val_fail},
            "events": len(data),
        }

    def timeseries_latency(self) -> Dict[str, Any]:
        # line chart: (ts, ms) per small/big
        small, big = [], []
        for e in self.recent(2000):
            if e.stage == "llm":
                row = {"t": e.ts, "ms": e.fields.get("latency_ms", 0)}
                (small if e.fields.get("tier") == "small" else big).append(row)
        return {"small": small, "big": big}

    def distribution_fail_reasons(self) -> Dict[str, int]:
        counts: Dict[str,int] = {}
        for e in self.recent(2000):
            if e.stage == "validate" and e.fields.get("ok") is False:
                why = (e.fields.get("why") or "unknown").lower()
                counts[why] = counts.get(why, 0) + 1
        return counts

    def tokens_timeseries(self) -> Dict[str, Any]:
        # area/line: out_tokens per tier
        small, big = [], []
        for e in self.recent(2000):
            if e.stage == "llm":
                row = {"t": e.ts, "tok": e.fields.get("out_tokens", 0)}
                (small if e.fields.get("tier") == "small" else big).append(row)
        return {"small": small, "big": big}

    def export_csv(self) -> str:
        # scaricabile da /api/metrics/export
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["ts","req_id","stage","key","value"])
        for e in self.recent(2000):
            base = [e.ts, e.req_id, e.stage]
            for k,v in e.fields.items():
                w.writerow(base+[k, v])
        return buf.getvalue()

STORE = TelemetryStore()
