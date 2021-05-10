import re
from pathlib import Path
from typing import Optional

from requests import Response


def strip_chars(value: str) -> str:
    """Strips '.', '-' and '/' from `value`."""
    return re.sub('[\.\-/]', '', value)


def sanitize_cpf(value: str) -> str:
    return strip_chars(value)


def sanitize_cnpj(value: str) -> str:
    return strip_chars(value)


def sanitize_cep(value: str) -> str:
    return strip_chars(value)


def check_file(path_str: str) -> Path:
    path = Path(path_str).resolve()

    if not path.exists() and not path.is_file():
        raise FileNotFoundError(f"'{path_str}' não é um arquivo válido.")

    return path


def check_response(response: Response,
                   additional_message: Optional[str] = None) -> dict:
    contents = response.json()
    if response.status_code != 200:
        api_err = contents['message']
        if additional_message is not None:
            msg = f"{additional_message}.\nMotivo: '{api_err}'"
        else:
            msg = api_err

        raise ValueError(msg)

    return contents
