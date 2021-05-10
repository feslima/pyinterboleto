import re


def strip_chars(value: str) -> str:
    """Strips '.', '-' and '/' from `value`."""
    return re.sub('[\.\-/]', '', value)


def sanitize_cpf(value: str) -> str:
    return strip_chars(value)


def sanitize_cnpj(value: str) -> str:
    return strip_chars(value)


def sanitize_cep(value: str) -> str:
    return strip_chars(value)
