from enum import Enum, unique
from json import dumps

from requests import post

from ..utils.requests import RequestConfigs, get_api_configs
from ..utils.url import API_URL


@unique
class CodigoBaixaEnum(Enum):
    """Domínio que descreve o tipo de baixa sendo solicitado.

    - A: Baixa por acertos;
    - P: Baixado por ter sido protestado;
    - D: Baixado para devolução;
    - PAB: Baixado por protesto após baixa;
    - PDC: Baixado, pago direto ao cliente;
    - S: Baixado por substituição;
    - FS: Baixado por falta de solução;
    - PC: Baixado a pedido do cliente;
    """
    A = 'ACERTOS'
    P = 'PROTESTADO'
    D = 'DEVOLUCAO'
    PAB = 'PROTESTOAPOSBAIXA'
    PDC = 'PAGODIRETOAOCLIENTE'
    S = 'SUBISTITUICAO'
    FS = 'FALTADESOLUCAO'
    PC = 'APEDIDODOCLIENTE'


def executa_baixa(nosso_numero: str, codigo_baixa: CodigoBaixaEnum,
                  configs: RequestConfigs) -> None:
    """Executa a baixa de um boleto.

    O registro da baixa é realizado no padrão D+1, ou seja, os boletos 
    baixados na data atual só serão baixados na base centralizada partir do 
    dia seguinte.

    Parameters
    ----------
    nosso_numero : str
        Número identificador do título.

    codigo_baixa : CodigoBaixaEnum
        Domínio que descreve o tipo de baixa sendo solicitado.

    configs: RequestConfigs
        Dicionário de configuração com número de conta e certificados de 
        autenticação.
    """
    acc, certificate, key = get_api_configs(configs)
    headers = {
        'Content-Type': 'application/json',
        'x-inter-conta-corrente': acc
    }

    URL = API_URL + f'/{nosso_numero}/baixas'
    data = dumps({'codigoBaixa': codigo_baixa.value})
    response = post(URL, data=data, headers=headers, cert=(certificate, key))

    if response.status_code != 204:
        raise ValueError(
            "Baixa de boleto não foi executada.\n"
            f"Motivo: '{response.json()['message']}'")
