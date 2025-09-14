import re

def _heuristic_complexity(topic: str) -> float:
    t = topic.lower()
    score = 0.0
    n = len(t)
    if n > 120: score += 0.2
    if n > 240: score += 0.2
    if re.search(r"\b(prova|dimostra|teorema|deriva|ottimizz|distributed|k8s|kubernetes|pytorch|tensor)\b", t):
        score += 0.4
    if re.search(r"\b(confronta|compara|trade[- ]off|architettura|pipeline)\b", t):
        score += 0.2
    if re.search(r"\b(definisci|spiega|cos'?è|overview)\b", t):
        score -= 0.1
    return max(0.0, min(1.0, score))

def route(topic: str, threshold: float = 0.6) -> dict:
    c = _heuristic_complexity(topic)
    if c < threshold:
        return {"target": "small", "confidence": 1 - c, "reason": f"complexity={c:.2f} < {threshold}"}
    return {"target": "big", "confidence": c, "reason": f"complexity={c:.2f} ≥ {threshold}"}
