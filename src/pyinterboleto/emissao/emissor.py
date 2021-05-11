from dataclasses import asdict, dataclass, field
from datetime import date
from enum import Enum
from json import JSONEncoder, dumps
from typing import Any, Dict, Literal, TypedDict, Union

from requests import post

from ..utils.floats import is_non_zero_positive_float, is_positive_float
from ..utils.requests import RequestConfigs, get_api_configs
from ..utils.sanitize import (ConvertDateMixin, check_response, sanitize_cnpj,
                              sanitize_cpf, strip_chars)
from ..utils.url import API_URL
from .desconto import SEM_DESCONTO_DICT, Desconto
from .mensagem import MENSAGEM_VAZIA, Mensagem
from .mora import SEM_MORA, CodigoMoraEnum, Mora
from .multa import SEM_MULTA, CodigoMultaEnum, Multa
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
NUM_DIAS_AGENDA = Literal['TRINTA', 'SESSENTA']


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

    seuNumero: str
        Campo Seu Número do título.

    cnpjCPFBeneficiario: str
        CPF/CNPJ do beneficiário do título.

    valorNominal: float
        Valor Nominal do título

    dataEmissao: Union[str, date]
        Data de emissão do título. Se o valor informado for do tipo str, terá
        que ser no formato AAAA-MM-DD (ISO8601), e será convertido para o tipo
        date.

    dataVencimento: Union[str, date]
        Data de vencimento do título. Se o valor informado for do tipo str, terá
        que ser no formato AAAA-MM-DD (ISO8601), e será convertido para o tipo
        date.

    valorAbatimento: float, optional
        Valor de abatimento do título, expresso na mesma moeda do 
        `valorNominal`. Caso não seja especificado, valor será 0.0.

    numDiasAgenda: Literal['TRINTA', 'SESSENTA'], optional
        Número de dias corridos após o vencimento para baixa efetiva automática 
        do boleto. Caso não seja especificado, valor será 'TRINTA'.

    mensagem: Mensagem, optional
        Mensagem a ser inserida no canhoto do boleto. Caso não seja especificado
        será usado um objeto que representa uma mensagem vazia. Isto é, todos 
        os campos serão em branco (string vazio).

    desconto1: Desconto, optional
        Desconto a ser aplicado ao título. Caso não seja especificado, será 
        definido um objeto de Desconto que há desconto. Isto é:
        {
            'codigoDesconto': 'NAOTEMDESCONTO', 
            'data': '', 
            'taxa': 0.0, 
            'valor': 0.0
        }

    desconto2: Desconto, optional
        Desconto a ser aplicado ao título. Caso não seja especificado, será 
        definido um objeto de Desconto que há desconto. Isto é:
        {
            'codigoDesconto': 'NAOTEMDESCONTO', 
            'data': '', 
            'taxa': 0.0, 
            'valor': 0.0
        }

    desconto3: Desconto, optional
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
    # mandatory fields
    pagador: Pagador
    seuNumero: str
    cnpjCPFBeneficiario: str
    valorNominal: float
    dataEmissao: Union[str, date]
    dataVencimento: Union[str, date]
    numDiasAgenda: NUM_DIAS_AGENDA = field(default='TRINTA')
    desconto1: Desconto = field(default=SEM_DESCONTO_DICT)
    desconto2: Desconto = field(default=SEM_DESCONTO_DICT)
    desconto3: Desconto = field(default=SEM_DESCONTO_DICT)
    multa: Multa = field(default=SEM_MULTA)
    mora: Mora = field(default=SEM_MORA)

    # optional fields
    valorAbatimento: float = 0.0
    mensagem: Mensagem = field(default=MENSAGEM_VAZIA)

    def __post_init__(self):
        assert len(self.seuNumero) <= 15 and self.seuNumero != ''

        self.cnpjCPFBeneficiario = strip_chars(self.cnpjCPFBeneficiario)
        if len(self.cnpjCPFBeneficiario) == 11:
            self.cnpjCPFBeneficiario = sanitize_cpf(self.cnpjCPFBeneficiario)
        else:
            self.cnpjCPFBeneficiario = sanitize_cnpj(self.cnpjCPFBeneficiario)

        assert len(self.cnpjCPFBeneficiario) == 14

        assert is_non_zero_positive_float(self.valorNominal)

        assert is_positive_float(self.valorAbatimento)

        self.convert_date('dataVencimento')
        self.convert_date('dataEmissao')
        assert self.dataVencimento >= self.dataEmissao

        if self.multa.codigoMulta != CodigoMultaEnum.NTM:
            assert self.multa.data > self.dataVencimento

        if self.mora.codigoMora != CodigoMoraEnum.I:
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


def emitir_boleto(dados: Emissao, configs: RequestConfigs) -> BoletoResponse:
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

    Returns
    -------
    BoletoResponse
        Dicionário que descreve o resultado de uma emissão de boleto bem 
        sucedida.
    """
    acc, certificate, key = get_api_configs(configs)
    headers = {
        'content-type': 'application/json',
        'x-inter-conta-corrente': acc
    }

    response = post(API_URL, data=dados.to_json(),
                    headers=headers,
                    cert=(certificate, key))

    contents = check_response(response, "Boleto não foi emitido")

    result = BoletoResponse(**contents)
    return result
