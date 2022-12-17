from base64 import b64decode
from io import BytesIO
from pathlib import Path

from requests import get

from ..auth import get_api_configs
from ..utils.requests import PathType, RequestConfigs
from ..utils.url import API_URL


def get_pdf_boleto_in_memory(
    nosso_numero: str, configs: RequestConfigs, token: str
) -> BytesIO:
    """Captura o boleto em um buffer na memória.

    Parameters
    ----------
    nosso_numero : str
        Número identificador do título.

    configs : RequestConfigs
        Dicionário de configuração com número de conta e certificados de
        autenticação.
    token : str
        Token de autenticação da API do Banco Inter. Veja:
        https://developers.bancointer.com.br/reference/obtertoken

    Returns
    -------
    BytesIO
        Objeto do tipo bytes. Já é decodificado (base64) e pronto pra manuseio.

    Raises
    ------
    ValueError
        Não foi possível obter uma resposta bem sucedida
    """
    certificate, key = get_api_configs(configs)

    headers = {"Authorization": f"Bearer {token}"}

    URL = API_URL + f"/{nosso_numero}/pdf"

    response = get(URL, headers=headers, cert=(certificate, key))

    if response.status_code != 200:
        raise ValueError("Não foi possível resgatar as informações do boleto.")

    return BytesIO(b64decode(response.content))


def get_pdf_boleto_to_file(
    nosso_numero: str, filename: PathType, configs: RequestConfigs, token: str
) -> None:
    """Salva o boleto em um arquivo .pdf.

    Parameters
    ----------
    nosso_numero : str
        Número identificador do título.

    filename : PathType
        Nome do arquivo a ser salvo.

    configs : RequestConfigs
        Dicionário de configuração com número de conta e certificados de
        autenticação.
    token : str
        Token de autenticação da API do Banco Inter. Veja:
        https://developers.bancointer.com.br/reference/obtertoken

    Raises
    ------
    FileExistsError
        Caminho de arquivo fornecido já existe.

    ValueError
        Extensão de arquivo fornecida não é do tipo .pdf.
    """
    filename = Path(filename).resolve()

    if filename.exists():
        raise FileExistsError("Um arquivo com este nome já existe.")

    if filename.suffix != ".pdf":
        raise ValueError("Extensão do arquivo deve ser .pdf.")

    pdf_bytes = get_pdf_boleto_in_memory(nosso_numero, configs, token)

    filename.write_bytes(pdf_bytes.getbuffer())
