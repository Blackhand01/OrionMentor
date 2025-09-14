from langchain.output_parsers import StructuredOutputParser, ResponseSchema

schemas = [
    ResponseSchema(name="explanation", description="Detailed explanation string"),
    ResponseSchema(name="steps", description="List of short action steps", type="list"),
    ResponseSchema(name="exercise", description="Object with question and expected_output"),
    ResponseSchema(name="sources", description="List of source strings", type="list"),
]
json_parser = StructuredOutputParser.from_response_schemas(schemas)
