from typing import Tuple

from requests import post

from .utils.requests import RequestConfigs, ScopeEnum
from .utils.sanitize import check_file


def build_auth_body(
    client_id: str, client_secret: str, scopes: Tuple[ScopeEnum, ...]
) -> str:
    scope_str = " ".join(s.value for s in scopes)
    return (
        f"client_id={str(client_id)}"
        f"&client_secret={str(client_secret)}"
        f"&scope={scope_str}"
        "&grant_type=client_credentials"
    )


AUTH_URL = "https://cdpj.partners.bancointer.com.br/oauth/v2/token"


def get_auth_token(configs: RequestConfigs) -> str:
    body = build_auth_body(
        configs["client_id"], configs["client_secret"], configs["scopes"]
    )
    response = post(
        AUTH_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=body,
    )
    if response.status_code == 403:
        raise ValueError(
            "Requisição de participante autenticado que viola alguma regra de "
            "autorização."
        )
    if response.status_code == 404:
        raise ValueError("Recurso solicitado não foi encontrado.")
    if response.status_code == 503:
        raise ValueError(
            "Serviço não está disponível no momento. Serviço solicitado "
            "pode estar em manutenção ou fora da janela de funcionamento."
        )
    data = response.json()
    return data["access_token"]


def get_api_configs(configs: RequestConfigs) -> Tuple[str, str, str]:
    certificate = str(check_file(configs["certificate"]))
    key = str(check_file(configs["key"]))
    auth_token = get_auth_token(configs)

    return auth_token, certificate, key
