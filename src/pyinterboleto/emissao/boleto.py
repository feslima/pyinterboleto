from pathlib import Path
from typing import TypedDict, Union

from requests import post

from ..utils.sanitize import strip_chars
from .emissor import Emissao

_API_URL = 'https://apis.bancointer.com.br:8443/openbanking/v1/certificado/boletos'


class BoletoResponse(TypedDict):
    seuNumero: str
    nossoNumero: str
    codigoBarras: str
    linhaDigitavel: str


PathType = Union[str, Path]


class Boleto:
    def __init__(self, dados: Emissao, conta_inter: str, cert_path: PathType,
                 key_path: PathType) -> None:
        self._conta_inter = strip_chars(conta_inter)
        self._dados = dados
        self._emitido: bool = False

        self._headers = {
            'content-type': 'application/json',
            'x-inter-conta-corrente': self.conta_inter
        }

        self._cert: Path = self._check_file(cert_path)
        self._key: Path = self._check_file(key_path)

    def _check_file(self, path_str: str) -> Path:
        path = Path(path_str).resolve()

        if not path.exists() and not path.is_file():
            raise FileNotFoundError(f"'{path_str}' não é um arquivo válido.")

        return path

    @property
    def dados(self) -> Emissao:
        return self._dados

    @property
    def emitido(self) -> bool:
        return self._emitido

    @property
    def conta_inter(self) -> str:
        return self._conta_inter

    @property
    def certificate(self) -> str:
        return str(self._cert)

    @property
    def key(self) -> str:
        return str(self._key)

    def emitir(self) -> BoletoResponse:
        response = post(_API_URL, data=self.dados.to_json(),
                        headers=self._headers,
                        cert=(self.certificate, self.key))

        contents = response.json()

        if response.status_code != 200:
            api_err = contents['message']
            msg = f"Boleto não foi emitido.\nMotivo: '{api_err}'"

            raise ValueError(msg)

        self._emitido = True
        return BoletoResponse(**contents)
