import jsonschema

STRICT_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["explanation", "steps", "exercise", "sources"],
    "properties": {
        "explanation": { "type": "string", "minLength": 80 },
        "steps": { "type": "array", "items": { "type": "string" }, "minItems": 2 },
        "exercise": {
            "type": "object",
            "required": ["question", "expected_output"],
            "properties": {
                "question": { "type": "string", "minLength": 10 },
                "expected_output": { "type": "string", "minLength": 5 }
            }
        },
        "sources": { "type": "array", "items": { "type": "string" }, "minItems": 1 }
    },
    "additionalProperties": False
}

def is_valid_response(resp: dict) -> tuple[bool, str]:
    try:
        jsonschema.validate(instance=resp, schema=STRICT_JSON_SCHEMA)
    except jsonschema.ValidationError as e:
        return False, f"jsonschema: {e.message}"
    expl = str(resp.get("explanation","")).strip()
    if "i don't know" in expl.lower():
        return False, "low confidence"
    return True, "ok"
