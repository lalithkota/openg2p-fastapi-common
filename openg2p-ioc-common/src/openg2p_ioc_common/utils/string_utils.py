import re


def convert_to_kebab_case(string: str):
    return re.sub(r"(?<!^)(?=[A-Z])", "-", string).replace("_", "-").lower()


def convert_to_snake_case(string: str):
    return re.sub(r"(?<!^)(?=[A-Z])", "-", string).replace("-", "_").lower()
