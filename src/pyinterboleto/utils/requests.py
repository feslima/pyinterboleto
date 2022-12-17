from enum import Enum, unique
from typing import Tuple, TypedDict

from .sanitize import PathType


@unique
class ScopeEnum(str, Enum):
    """Escopos disponíveis:

    extrato.read - Consulta de Extrato e Saldo
    boleto-cobranca.read - Consulta de boletos e exportação para PDF
    boleto-cobranca.write - Emissão e cancelamento de boletos
    pagamento-boleto.write - Pagamento de titulo com código de barras
    pagamento-boleto.read - Obter dados completos do titulo a partir do código de
    barras ou da linha digitável
    pagamento-darf.write - Pagamento de DARF sem código de barras
    """

    EXTRATO_READ = "extrato.read"
    BOLETO_COBRANCA_READ = "boleto-cobranca.read"
    BOLETO_COBRANCA_WRITE = "boleto-cobranca.write"
    PAGAMENTO_BOLETO_READ = "pagamento-boleto.read"
    PAGAMENTO_BOLETO_WRITE = "pagamento-boleto.write"
    PAGAMENTO_DARF_WRITE = "pagamento-darf.write"

    @classmethod
    def get_all_scopes(cls) -> Tuple["ScopeEnum", ...]:
        return tuple(cls)


class RequestConfigs(TypedDict):
    """Dicionário contendo as configurações necessárias para se comunicar com a
    API do banco Inter.

    Parameters
    ----------
    client_id: str
        Client Id obtido no detalhe da tela de aplicações no IB.

    client_secret: str
        Client Secret obtido no detalhe da tela de aplicações no IB.

    scopes: Tuple[ScopeEnum,...]
        Escopos cadastrados na tela de aplicações.
        OBS: No caso de precisar adicionar mais de um escopo, os escopos devem ser
        separados com espaço (extrato.read boleto-cobranca.read)

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
    >>> from pyinterboleto import RequestConfigs, ScopeEnum
    >>> direc = Path('caminho/para/pasta/com/certificados')
    >>> cert = direc / 'Inter API_Certificado.crt'
    >>> key = direc / 'Inter API_Chave.key'
    >>> # client_id e client_secret são obtidos de acordo com a documentação do Inter
    >>> client_id = 'valor-do-id-uuid'
    >>> client_secret = 'valor-do-secret-uuid'
    >>> scopes = (ScopeEnum.EXTRATO_READ, ScopeEnum.BOLETO_COBRANCA_READ)
    >>> configs = RequestConfigs(client_id=client_id, client_secret=client_secret, scopes=scopes, certificate=cert, key=key)
    >>> pprint(configs)
    {'certificate': PosixPath('caminho/para/pasta/com/certificados/Inter API_Certificado.crt'),
     'client_id': 'valor-do-id-uuid',
     'client_secret': 'valor-do-secret-uuid',
     'scopes': (ScopeEnum.EXTRATO_READ, ScopeEnum.BOLETO_COBRANCA_READ),
     'key': PosixPath('caminho/para/pasta/com/certificados/Inter API_Chave.key')}

    """

    client_id: str
    client_secret: str
    scopes: Tuple[ScopeEnum, ...]
    certificate: PathType
    key: PathType
