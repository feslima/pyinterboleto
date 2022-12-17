import re
from datetime import date, datetime
from pathlib import Path
from typing import Optional, Union

from requests import Response

PathType = Union[str, Path]


def strip_chars(value: str) -> str:
    """Strips non numeric values from `value`."""
    return re.sub(r"\D", "", value)


def sanitize_cpf(value: str) -> str:
    return strip_chars(value)


def sanitize_cnpj(value: str) -> str:
    return strip_chars(value)


def sanitize_cep(value: str) -> str:
    return strip_chars(value)


def check_file(path_str: PathType) -> Path:
    path = Path(path_str).resolve()

    if not path.exists() and not path.is_file():
        raise FileNotFoundError(f"'{path_str}' não é um arquivo válido.")

    return path


def check_response(
    response: Response, additional_message: Optional[str] = None
) -> dict:
    contents = response.json()
    if response.status_code != 200:
        api_err = contents["message"]
        if additional_message is not None:
            msg = f"{additional_message}.\nMotivo: '{api_err}'"
        else:
            msg = api_err

        raise ValueError(msg)

    return contents


def str_to_date(value: str) -> date:
    """Converts a string representation of a date in YYYY-MM-DD format into
    date object."""
    return datetime.strptime(value, "%Y-%m-%d").date()


def str_to_datetime(value: str) -> datetime:
    """Converts a string representation of a datetime in dd/mm/YYYY HH:MM
    format into datetime object."""
    return datetime.strptime(value, "%Y-%m-%d %H:%M")


class ConvertDateMixin:
    """Habilita conversão de campos do tipo str em tipo date.

    Formato do str deve ser dd/mm/AAAA"""

    def convert_date(self, field: str) -> None:
        value = getattr(self, field)
        if isinstance(value, str) and value:
            setattr(self, field, str_to_date(value))


class ConvertDatetimeMixin:
    """Habilita conversão de campos do tipo str em tipo datetime.

    Formato do str deve ser dd/mm/AAAA HH:MM"""

    def convert_datetime(self, field: str) -> None:
        value = getattr(self, field)
        if isinstance(value, str) and value:
            setattr(self, field, str_to_datetime(value))
