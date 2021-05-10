from base64 import b64decode
from io import BytesIO
from pathlib import Path

from pyinterboleto.utils.requests import PathType, RequestConfigs
from pyinterboleto.utils.sanitize import check_file, strip_chars
from requests import get

_API_URL = 'https://apis.bancointer.com.br:8443/openbanking/v1/certificado/boletos'


def get_pdf_boleto_in_memory(nosso_numero: str, configs: RequestConfigs) \
        -> BytesIO:
    """Captura o boleto em um buffer na memória.

    Returns
    -------
    BytesIO
        Bytes-like object. Already decoded from base64.

    Raises
    ------
    ValueError
        Não foi possível obter uma resposta bem sucedida
    """
    headers = {'x-inter-conta-corrente': strip_chars(configs['conta_inter'])}
    cert = str(check_file(configs['cert']))
    key = str(check_file(configs['key']))

    URL = _API_URL + f'/{nosso_numero}/pdf'

    response = get(URL, headers=headers, cert=(cert, key))

    if response.status_code != 200:
        raise ValueError("Não foi possível resgatar as informações do boleto.")

    return BytesIO(b64decode(response.content))


def get_pdf_boleto_to_file(nosso_numero: str, filename: PathType,
                           configs: RequestConfigs) -> None:
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

    Raises
    ------
    FileExistsError
        Caminho de arquivo fornecido já existe.
    """
    filename = Path(filename).resolve()

    if filename.exists():
        raise FileExistsError("Um arquivo com este nome já existe.")

    pdf_bytes = get_pdf_boleto_in_memory(nosso_numero, configs)

    filename.write_bytes(pdf_bytes.getbuffer())
