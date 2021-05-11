from pathlib import Path
from typing import TypedDict

from requests import get

from ..emissao.desconto import Desconto
from ..emissao.mora import Mora
from ..emissao.multa import Multa
from ..utils.requests import RequestConfigs, get_api_configs
from ..utils.sanitize import check_response
from ..utils.url import API_URL


class BoletoDetail(TypedDict):
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
    situacaoPagamento: str
    desconto1: Desconto
    desconto2: Desconto
    desconto3: Desconto
    multa: Multa
    mora: Mora


def _rename_dict_key(d: dict, old_key: str, new_key: str) -> dict:
    d[new_key] = d[old_key]
    del d[old_key]
    return d


def convert_contents_into_detail(contents: dict) -> BoletoDetail:
    d1 = _rename_dict_key(contents.pop('desconto1'),
                          'codigo', 'codigoDesconto')
    d2 = _rename_dict_key(contents.pop('desconto2'),
                          'codigo', 'codigoDesconto')
    d3 = _rename_dict_key(contents.pop('desconto3'),
                          'codigo', 'codigoDesconto')
    desconto1 = Desconto(**d1)
    desconto2 = Desconto(**d2)
    desconto3 = Desconto(**d3)

    m = _rename_dict_key(contents.pop('multa'), 'codigo', 'codigoMulta')
    multa = Multa(**m)

    m = _rename_dict_key(contents.pop('mora'), 'codigo', 'codigoMora')
    mora = Mora(**m)

    return BoletoDetail(mora=mora, multa=multa,
                        desconto1=desconto1, desconto2=desconto2,
                        desconto3=desconto3, **contents)


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

    return convert_contents_into_detail(contents)
