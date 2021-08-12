from dataclasses import dataclass

from dacite import from_dict
from requests import get

from ..common.desconto import DescontoConsulta
from ..common.mora import MoraConsulta
from ..common.multa import MultaConsulta
from ..utils.requests import RequestConfigs, get_api_configs
from ..utils.sanitize import check_response
from ..utils.url import API_URL


@dataclass
class BoletoDetail:
    """Dicionário de respresentação de um boleto detalhado."""
    nomeBeneficiario: str
    cnpjCpfBeneficiario: str
    tipoPessoaBeneficiario: str
    dataHoraSituacao: str
    codigoBarras: str
    linhaDigitavel: str
    dataVencimento: str
    dataEmissao: str
    descricao: str
    seuNumero: str
    valorNominal: float
    nomePagador: str
    emailPagador: str
    telefonePagador: str
    tipoPessoaPagador: str
    cnpjCpfPagador: str
    dataLimitePagamento: str
    valorAbatimento: float
    situacao: str
    desconto1: DescontoConsulta
    desconto2: DescontoConsulta
    desconto3: DescontoConsulta
    multa: MultaConsulta
    mora: MoraConsulta


def get_boleto_detail(nosso_numero: str, configs: RequestConfigs) \
        -> BoletoDetail:
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
        Dicionário de representação detalhada de um boleto.
    """
    acc, certificate, key = get_api_configs(configs)

    headers = {'x-inter-conta-corrente': acc}

    URL = API_URL + f'/{nosso_numero}'
    response = get(URL, headers=headers, cert=(certificate, key))

    contents = check_response(response, "Boleto não encontrado.")

    return from_dict(BoletoDetail, contents)
