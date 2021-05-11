
from pathlib import Path
from typing import Tuple, TypedDict, Union

from .sanitize import check_file, strip_chars

PathType = Union[str, Path]


class RequestConfigs(TypedDict):
    """Dicionário contendo as configurações necessárias para se comunicar com a 
    API do banco Inter.

    Parameters
    ----------
    conta_inter: str
        Número da conta PJ.

    certificate: PathType
        Caminho para o arquivo de certificado (.crt) que é emitido de acordo 
        com a documentação no site do banco Inter.

    key: PathType
        Caminho para o arquivo de chave (.key) que é emitido de acordo com a 
        documentação no site do banco Inter.

    Examples
    --------
    Exemplo de como definir um objeto de configuração:

    >>> from pathlib import Path
    >>> from pprint import pprint
    >>> from pyinterboleto import RequestConfigs
    >>> direc = Path('caminho/para/pasta/com/certificados')
    >>> cert = direc / 'Inter API_Certificado.crt'
    >>> key = direc / 'Inter API_Chave.key'
    >>> acc = '12345678' # número da conta Inter PJ incluindo dígito
    >>> configs = RequestConfigs(conta_inter=acc, certificate=cert, key=key)
    >>> pprint(configs)
    {'certificate': PosixPath('caminho/para/pasta/com/certificados/Inter API_Certificado.crt'),
     'conta_inter': '12345678',
     'key': PosixPath('caminho/para/pasta/com/certificados/Inter API_Chave.key')}

    """
    conta_inter: str
    certificate: PathType
    key: PathType


def get_api_configs(configs: RequestConfigs) -> Tuple[str, Path, Path]:
    certificate = str(check_file(configs['certificate']))
    key = str(check_file(configs['key']))
    acc = strip_chars(configs['conta_inter'])

    return acc, certificate, key
