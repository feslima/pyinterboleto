from pathlib import Path
from typing import TypedDict

from requests import post

from ..utils.requests import RequestConfigs
from ..utils.sanitize import check_file, check_response, strip_chars
from .emissor import Emissao

_API_URL = 'https://apis.bancointer.com.br:8443/openbanking/v1/certificado/boletos'


class BoletoResponse(TypedDict):
    """Dicionário que descreve o resultado de uma emissão de boleto bem 
    sucedida.

    Parameters
    ----------
    seuNumero: str
        Seu Número enviado na requisição para inclusão do título.

    nossoNumero: str
        Nosso Número atribuído automaticamente ao longo da inclusão do título.

    codigoBarras: str
        44 posições preenchidas com os dígitos que compõem o código de barras 
        do boleto.

    linhaDigitavel: str
        47 posições preenchidas com os dígitos que compõem a linha digitável do 
        boleto, sem formatação.

    """
    seuNumero: str
    nossoNumero: str
    codigoBarras: str
    linhaDigitavel: str


class Boleto:
    def __init__(self, dados: Emissao, configs: RequestConfigs) -> None:
        self._conta_inter = strip_chars(configs['conta_inter'])
        self._dados = dados
        self._emitido: bool = False
        self._numero: str = ''

        self._headers = {
            'content-type': 'application/json',
            'x-inter-conta-corrente': self.conta_inter
        }

        self._cert: Path = check_file(configs['cert'])
        self._key: Path = check_file(configs['key'])

    @property
    def dados(self) -> Emissao:
        return self._dados

    @property
    def emitido(self) -> bool:
        return self._emitido

    @property
    def numero(self) -> str:
        """Número de identificação que identifica o boleto na API.

        Se o boleto ainda não foi emitido, essa propriedade é um string vazio.
        """
        return self._numero

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

        contents = check_response(response, "Boleto não foi emitido")

        result = BoletoResponse(**contents)
        self._emitido = True
        self._numero = result['nossoNumero']
        return result
