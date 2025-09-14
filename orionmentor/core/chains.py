from langchain_core.runnables import RunnableMap
from orionmentor.core.prompts import EXPLANATION_PROMPT, FORMAT_INSTRUCTIONS
from orionmentor.core.parsers import json_parser
from orionmentor.config import settings
from orionmentor.core.models.openai_provider import OpenAIProvider
from orionmentor.core.router import route
from orionmentor.core.validator import is_valid_response
from orionmentor.core.telemetry.logger import timed_call, log_event

def get_provider(model=None):
    p = (settings.MODEL_PROVIDER or "openai").lower()
    m = model or settings.MODEL_NAME
    if p == "openai":
        return OpenAIProvider(model=m)
    raise ValueError(f"Unknown provider: {settings.MODEL_PROVIDER}")

def build_chain():
    provider = get_provider()
    def _invoke_llm(prompt):
        if hasattr(prompt, "to_string"):
            prompt = prompt.to_string()
        elif not isinstance(prompt, str):
            prompt = str(prompt)
        return provider.invoke(prompt)

    inputs = RunnableMap({
        "topic": lambda x: x,
        "format_instructions": lambda _: FORMAT_INSTRUCTIONS
    })

    chain = (
        inputs
        | EXPLANATION_PROMPT
        | _invoke_llm
        | json_parser
    )
    return chain

def build_chain_router():
    import uuid
    from orionmentor.core.telemetry.logger import estimate_tokens

    def _coerce_to_str(prompt):
        if hasattr(prompt, "to_string"):
            return prompt.to_string()
        elif not isinstance(prompt, str):
            return str(prompt)
        return prompt

    def _get_small_provider():
        return get_provider(settings.MODEL_NAME)

    def _get_big_provider():
        return get_provider(getattr(settings, "MODEL_NAME_BIG", "gpt-4o"))

    def _llm_call(provider, prompt):
        return provider.invoke(prompt)

    def _orchestrate(topic: str):
        req_id = uuid.uuid4().hex[:8]
        fmt = FORMAT_INSTRUCTIONS

        # ROUTE
        r = route(topic, threshold=getattr(settings, "ROUTER_THRESHOLD", 0.6))
        log_event("route", req_id=req_id, target=r["target"], conf=round(r["confidence"],2), reason=r["reason"])

        prompt_val = EXPLANATION_PROMPT.format(topic=topic, format_instructions=fmt)
        prompt_str = _coerce_to_str(prompt_val)
        log_event("prompt", req_id=req_id, in_tokens=estimate_tokens(prompt_str))

        if r["target"] == "small":
            small = _get_small_provider()
            txt, ms = timed_call(_llm_call, small, prompt_str)
            log_event("llm", req_id=req_id, tier="small", provider=small.name, latency_ms=int(ms), out_tokens=estimate_tokens(txt))
            try:
                resp = json_parser.parse(txt)
            except Exception as e:
                log_event("parse", req_id=req_id, tier="small", error=str(e)[:120])
                resp = None

            if resp:
                ok, why = is_valid_response(resp)
                log_event("validate", req_id=req_id, tier="small", ok=ok, why=why)
                if ok:
                    return resp | {"_meta": {"provider_tier":"small","route_reason":r["reason"],"req_id":req_id}}

        big = _get_big_provider()
        txt2, ms2 = timed_call(_llm_call, big, prompt_str)
        log_event("llm", req_id=req_id, tier="big", provider=big.name, latency_ms=int(ms2), out_tokens=estimate_tokens(txt2))
        resp2 = json_parser.parse(txt2)
        ok2, why2 = is_valid_response(resp2)
        log_event("validate", req_id=req_id, tier="big", ok=ok2, why=why2)
        return resp2 | {"_meta": {"provider_tier":"big","route_reason":r["reason"],"req_id":req_id}}

    return _orchestrate
