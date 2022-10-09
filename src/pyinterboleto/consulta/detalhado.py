from dataclasses import dataclass
from datetime import date, datetime
from typing import Union

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
class BoletoDetail(ConvertDateMixin, ConvertDatetimeMixin):
    """Objeto de respresentação de um boleto detalhado."""

    nomeBeneficiario: str
    cnpjCpfBeneficiario: str
    tipoPessoaBeneficiario: str
    dataHoraSituacao: Union[datetime, str]
    codigoBarras: str
    linhaDigitavel: str
    dataVencimento: Union[date, str]
    dataEmissao: Union[date, str]
    seuNumero: str
    valorNominal: float
    nomePagador: str
    emailPagador: str
    dddPagador: str
    telefonePagador: str
    tipoPessoaPagador: str
    cnpjCpfPagador: str
    codigoEspecie: str
    dataLimitePagamento: Union[date, str]
    valorAbatimento: float
    situacao: str
    desconto1: DescontoConsulta
    desconto2: DescontoConsulta
    desconto3: DescontoConsulta
    multa: MultaConsulta
    mora: MoraConsulta
    situacaoPagamento: str = ""
    valorTotalRecebimento: float = 0.0

    def __post_init__(self):
        self.convert_date("dataVencimento")
        self.convert_date("dataEmissao")
        self.convert_date("dataLimitePagamento")

        self.convert_datetime("dataHoraSituacao")


def get_boleto_detail(nosso_numero: str, configs: RequestConfigs) -> BoletoDetail:
    """Recupera as informações de um boleto.

    Está pesquisa retorna as informações de um boleto no padrão D+0, ou seja,
    as informações do boleto são consultadas diretamente na CIP refletindo a
    situação em tempo real.

    Parameters
    ----------
    nosso_numero : str
        Número identificador do título.
    configs : RequestConfigs
        Dicionário de configuração com número de conta e certificados de
        autenticação.

    Returns
    -------
    BoletoDetail
        Objeto de representação detalhada de um boleto.
    """
    token, certificate, key = get_api_configs(configs)

    headers = {"Authorization": f"Bearer {token}"}

    URL = API_URL + f"/{nosso_numero}"
    response = get(URL, headers=headers, cert=(certificate, key))

    contents = check_response(response, "Boleto não encontrado.")

    return from_dict(BoletoDetail, contents)
