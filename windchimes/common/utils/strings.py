import re


camel_case_pattern = re.compile(r"(?<!^)(?=[A-Z])")


def convert_to_snake_case(camel_case_text: str):
    """converts CamelCase text to snake_case"""
    return camel_case_pattern.sub("_", camel_case_text).lower()
