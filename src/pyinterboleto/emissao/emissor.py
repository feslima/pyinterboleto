from dataclasses import asdict, dataclass, field
from datetime import date
from enum import Enum
from json import JSONEncoder, dumps
from typing import Any, Dict, TypedDict, Union

from requests import post

from ..auth import get_api_configs
from ..common.desconto import CodigoDescontoEnum, DescontoEmissao
from ..common.mora import CodigoMoraEnum, MoraEmissao
from ..common.multa import CodigoMultaEnum, MultaEmissao
from ..utils.floats import is_non_zero_positive_float
from ..utils.requests import RequestConfigs
from ..utils.sanitize import ConvertDateMixin, check_response
from ..utils.url import API_URL
from .beneficiario import Beneficiario
from .mensagem import MENSAGEM_VAZIA, Mensagem
from .pagador import Pagador


class DefaultEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Enum):
            return o.value
        elif isinstance(o, date):
            return o.isoformat()
        else:
            return super().default(o)


SerializedDict = Dict[str, Union[str, float]]


SEM_DESCONTO_DICT = DescontoEmissao(codigoDesconto=CodigoDescontoEnum.NAO_TEM_DESCONTO)
SEM_MORA = MoraEmissao(codigoMora=CodigoMoraEnum.ISENTO)
SEM_MULTA = MultaEmissao(codigoMulta=CodigoMultaEnum.NAO_TEM_MULTA)


@dataclass
class Emissao(ConvertDateMixin):
    """Estrutura que representa o detalhamento dos dados necessários para a
    emissão de um boleto.

    Os campos não obrigatórios (e.g. `desconto1`, `multa`, etc.) já são
    preenchidos com algumas configurações padrão.

    Parameters
    ----------
    pagador: Pagador
        Dados do pagador.

    beneficiario: Beneficiario
        Dados do beneficiário final.

    seuNumero: str
        Campo Seu Número do título.

    valorNominal: float
        Valor Nominal do título.

    dataVencimento: Union[str, date]
        Data de vencimento do título. Se o valor informado for do tipo str, terá
        que ser no formato AAAA-MM-DD (ISO8601), e será convertido para o tipo
        date.

    numDiasAgenda: int
        Número de dias corridos após o vencimento para cancelamento efetivo automático
        do boleto. Valor minimo 0, valor máximo 60 dias.

    mensagem: Mensagem, optional
        Mensagem a ser inserida no canhoto do boleto. Caso não seja especificado
        será usado um objeto que representa uma mensagem vazia. Isto é, todos
        os campos serão em branco (string vazio).

    desconto1: DescontoEmissao, optional
        Desconto a ser aplicado ao título. Caso não seja especificado, será
        definido um objeto de Desconto que há desconto. Isto é:
        {
            'codigoDesconto': 'NAOTEMDESCONTO',
            'data': '',
            'taxa': 0.0,
            'valor': 0.0
        }

    desconto2: DescontoEmissao, optional
        Desconto a ser aplicado ao título. Caso não seja especificado, será
        definido um objeto de Desconto que há desconto. Isto é:
        {
            'codigoDesconto': 'NAOTEMDESCONTO',
            'data': '',
            'taxa': 0.0,
            'valor': 0.0
        }

    desconto3: DescontoEmissao, optional
        Desconto a ser aplicado ao título. Caso não seja especificado, será
        definido um objeto de Desconto que há desconto. Isto é:
        {
            'codigoDesconto': 'NAOTEMDESCONTO',
            'data': '',
            'taxa': 0.0,
            'valor': 0.0
        }

    multa: Multa, optional
        Multa a ser aplicada ao título. Caso não seja especificado, será
        definido um objeto de Multa que há multa. Isto é:
        {
            'codigoMulta': 'NAOTEMMULTA',
            'data': '',
            'taxa': 0.0,
            'valor': 0.0
        }

    mora: Mora, optional
        Mora a ser aplicada ao título. Caso não seja especificado, será
        definido um objeto de Mora que há mora. Isto é:
        {
            'codigoMora': 'ISENTO',
            'data': '',
            'taxa': 0.0,
            'valor': 0.0
        }

    """

    pagador: Pagador
    beneficiario: Beneficiario
    seuNumero: str
    valorNominal: float
    dataVencimento: Union[str, date]
    numDiasAgenda: int
    mensagem: Mensagem = field(default=MENSAGEM_VAZIA)
    desconto1: DescontoEmissao = field(default=SEM_DESCONTO_DICT)
    desconto2: DescontoEmissao = field(default=SEM_DESCONTO_DICT)
    desconto3: DescontoEmissao = field(default=SEM_DESCONTO_DICT)
    multa: MultaEmissao = field(default=SEM_MULTA)
    mora: MoraEmissao = field(default=SEM_MORA)

    def __post_init__(self):
        assert 1 <= len(self.seuNumero) <= 15

        assert is_non_zero_positive_float(self.valorNominal)

        self.convert_date("dataVencimento")

        if self.multa.codigoMulta != CodigoMultaEnum.NAO_TEM_MULTA:
            assert self.multa.data > self.dataVencimento

        if self.mora.codigoMora != CodigoMoraEnum.ISENTO:
            assert self.mora.data > self.dataVencimento

    def to_dict(self) -> Dict[str, Union[str, float, SerializedDict]]:
        return asdict(self)

    def to_json(self) -> str:
        return dumps(self.to_dict(), cls=DefaultEncoder)


class BoletoResponse(TypedDict):
    """Dicionário que descreve o resultado de uma emissão de boleto bem
    sucedida.

    Parameters
    ----------
    seuNumero: str
        Seu Número enviado na requisição para inclusão do título.

    nossoNumero: str
        Nosso Número atribuído automaticamente ao longo da inclusão do título.

    codigoBarras: str
        44 posições preenchidas com os dígitos que compõem o código de barras
        do boleto.

    linhaDigitavel: str
        47 posições preenchidas com os dígitos que compõem a linha digitável do
        boleto, sem formatação.

    """

    seuNumero: str
    nossoNumero: str
    codigoBarras: str
    linhaDigitavel: str


def emitir_boleto(
    dados: Emissao, configs: RequestConfigs, token: str
) -> BoletoResponse:
    """Emite um boleto baseado nos `dados` provisionados.

    O boleto incluído estará disponível para consulta e pagamento, após
    um tempo apróximado de 5 minutos da sua inclusão. Esse tempo é
    necessário para o registro do boleto na CIP.

    Parameters
    ----------
    dados : Emissao
        Estrutura que representa o detalhamento dos dados necessários para
        a emissão de um boleto.

    configs: RequestConfigs
        Dicionário de configuração com número de conta e certificados de
        autenticação.

    token : str
        Token de autenticação da API do Banco Inter. Veja:
        https://developers.bancointer.com.br/reference/obtertoken

    Returns
    -------
    BoletoResponse
        Dicionário que descreve o resultado de uma emissão de boleto bem
        sucedida.
    """
    certificate, key = get_api_configs(configs)
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    response = post(
        API_URL, data=dados.to_json(), headers=headers, cert=(certificate, key)
    )

    contents = check_response(response, "Boleto não foi emitido")

    result = BoletoResponse(**contents)
    return result
