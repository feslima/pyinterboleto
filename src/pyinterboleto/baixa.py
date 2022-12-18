from enum import Enum, unique

from requests import post

from .auth import get_api_configs
from .exceptions import PyInterBoletoException
from .utils.requests import RequestConfigs
from .utils.url import API_URL


@unique
class MotivoCancelamentoEnum(Enum):
    """Domínio que descreve o tipo de cancelamento sendo solicitado.

    - ACERTOS (cancelado por acertos)
    - APEDIDODOCLIENTE (cancelado a pedido do cliente)
    - PAGODIRETOAOCLIENTE (cancelado por ter sido pago direto ao cliente)
    - SUBSTITUICAO (cancelado por substituição)
    """

    ACERTOS = "ACERTOS"
    PAGO_DIRETO_AO_CLIENTE = "PAGODIRETOAOCLIENTE"
    SUBSTITUICAO = "SUBSTITUICAO"
    A_PEDIDO_DO_CLIENTE = "APEDIDODOCLIENTE"


def cancelar_boleto(
    nosso_numero: str,
    motivo: MotivoCancelamentoEnum,
    configs: RequestConfigs,
    token: str,
) -> None:
    """Executa a baixa de um boleto.

    O registro da baixa é realizado no padrão D+1, ou seja, os boletos
    baixados na data atual só serão baixados na base centralizada partir do
    dia seguinte.

    Parameters
    ----------
    nosso_numero : str
        Número identificador do título.

    motivo : MotivoCancelamentoEnum
        Domínio que descreve o tipo de baixa sendo solicitado.

    configs: RequestConfigs
        Dicionário de configuração com número de conta e certificados de
        autenticação.

    token : str
        Token de autenticação da API do Banco Inter. Veja:
        https://developers.bancointer.com.br/reference/obtertoken
    """
    certificate, key = get_api_configs(configs)
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    URL = API_URL + f"/{nosso_numero}/cancelar"
    data = {"motivoCancelamento": motivo.value}
    response = post(URL, json=data, headers=headers, cert=(certificate, key))

    if response.status_code != 204:
        raise PyInterBoletoException(
            "Baixa de boleto não foi executada.\n"
            f"Motivo: '{response.json()['message']}'"
        )
