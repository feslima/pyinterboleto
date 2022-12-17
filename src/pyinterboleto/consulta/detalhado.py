from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Union

from dacite.core import from_dict
from requests import get

from ..auth import get_api_configs
from ..common.desconto import DescontoConsulta
from ..common.mora import MoraConsulta
from ..common.multa import MultaConsulta
from ..utils.requests import RequestConfigs
from ..utils.sanitize import ConvertDateMixin, ConvertDatetimeMixin, check_response
from ..utils.url import API_URL


@dataclass
class BoletoPagador:
    """Objeto de respresentação de um pagador boleto detalhado."""

    cpfCnpj: str
    tipoPessoa: str
    nome: str
    endereco: str
    numero: str
    complemento: str
    bairro: str
    cidade: str
    uf: str
    cep: str
    email: str
    ddd: str
    telefone: str


@dataclass
class BoletoDetail(ConvertDateMixin, ConvertDatetimeMixin):
    """Objeto de respresentação de um boleto detalhado."""

    nomeBeneficiario: str
    cnpjCpfBeneficiario: str
    tipoPessoaBeneficiario: str
    contaCorrente: str
    nossoNumero: str
    seuNumero: str
    pagador: BoletoPagador
    motivoCancelamento: str
    situacao: str
    dataHoraSituacao: Union[datetime, str]
    dataVencimento: Union[date, str]
    valorNominal: float
    dataEmissao: Union[date, str]
    dataLimite: Union[date, str]
    codigoEspecie: str
    codigoBarras: str
    linhaDigitavel: str
    origem: str
    mensagem: Dict[str, str]
    desconto1: DescontoConsulta
    desconto2: DescontoConsulta
    desconto3: DescontoConsulta
    multa: MultaConsulta
    mora: MoraConsulta

    def __post_init__(self):
        self.convert_date("dataVencimento")
        self.convert_date("dataEmissao")
        self.convert_date("dataLimite")

        self.convert_datetime("dataHoraSituacao")


def get_boleto_detail(
    nosso_numero: str, configs: RequestConfigs, token: str
) -> BoletoDetail:
    """Recupera as informações de um boleto.

    Esta pesquisa retorna as informações de um boleto no padrão D+0, ou seja,
    as informações do boleto são consultadas diretamente na CIP refletindo a
    situação em tempo real.

    Parameters
    ----------
    nosso_numero : str
        Número identificador do título.
    configs : RequestConfigs
        Dicionário de configuração com número de conta e certificados de autenticação.
    token : str
        Token de autenticação da API do Banco Inter. Veja:
        https://developers.bancointer.com.br/reference/obtertoken

    Returns
    -------
    BoletoDetail
        Objeto de representação detalhada de um boleto.
    """
    certificate, key = get_api_configs(configs)

    headers = {"Authorization": f"Bearer {token}"}

    url = f"{API_URL}/{nosso_numero}"
    response = get(url, headers=headers, cert=(certificate, key))

    contents = check_response(response, "Boleto não encontrado.")

    return from_dict(BoletoDetail, contents)
