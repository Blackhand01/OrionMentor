from langchain.prompts import PromptTemplate
from orionmentor.core.parsers import json_parser

STRICT_JSON_SCHEMA = '''
{
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
    "additionalProperties": false
}
'''

FORMAT_INSTRUCTIONS = (
        json_parser.get_format_instructions() +
        "\nSTRICT JSON SCHEMA (for validation):\n" + STRICT_JSON_SCHEMA
)

EXPLANATION_PROMPT = PromptTemplate.from_template(
    """You are OrionMentor, a precise AI tutor.
Return STRICT JSON with keys: explanation, steps, exercise, sources.
{format_instructions}

Topic: {topic}

In "explanation", write Markdown with:
- A level-2 title (## ...)
- Short intro paragraph
- A bulleted list of key points
- One code block if relevant (```python ... ```)
- One callout using :::note ... ::: for an insight
- Subheadings (###) where it improves readability

JSON only. No extra text."""
)
