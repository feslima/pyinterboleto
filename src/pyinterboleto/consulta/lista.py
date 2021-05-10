from dataclasses import dataclass
from datetime import date
from enum import Enum, unique
from typing import List, Optional, TypedDict, Union

from pyinterboleto.utils.requests import RequestConfigs
from requests import get

from ..emissao.desconto import Desconto
from ..emissao.mora import Mora
from ..emissao.multa import Multa
from ..utils.sanitize import (check_file, check_response, str_to_date,
                              strip_chars)

_API_URL = 'https://apis.bancointer.com.br:8443/openbanking/v1/certificado/boletos'


@unique
class FiltrarEnum(Enum):
    """Enum para situação atual do boleto para filtro.

    - T: Todos os títulos do cliente no período;
    - V: Todos os títulos a vencer/vencidos do cliente no período;
    - E: Todos os títulos expirados (não passível de pagamento) no período;
    - P: Todos os títulos pagos em condições normais do cliente no período;
    - TB: Todas as demais baixas do cliente no período;
    """
    T = 'TODOS'
    V = 'VENCIDOSAVENCER'
    E = 'EXPIRADOS'
    P = 'PAGOS'
    TB = 'TODOSBAIXADOS'


@unique
class OrdenarEnum(Enum):
    """Enum para ordenação do retorno da consulta.

    - NN: Nosso número (usado também para consulta do PDF do boleto);
    - SN: Seu número (que você usou na emissão);
    - DVA: Data de vencimento crescente;
    - DVD: Data de vencimento decrescente;
    - NS: Nome do sacado;
    - VA: Valor do título crescente;
    - VD: Valor do título decrescente;
    - SA: Status do título crescente;
    - SD: Status do título decrescente;
    """
    NN = 'NOSSONUMERO'
    SN = 'SEUNUMERO'
    DVA = 'DATAVENCIMENTO_ASC'
    DVD = 'DATAVENCIMENTO_DSC'
    NS = 'NOMESACADO'
    VA = 'VALOR_ASC'
    VD = 'VALOR_DSC'
    SA = 'STATUS_ASC'
    SD = 'STATUS_DSC'


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


@dataclass
class BoletoItem:
    nossoNumero: str
    seuNumero: str
    cnpjCpfSacado: str
    nomeSacado: str
    codigoBaixa: Union[str, CodigoBaixaEnum]
    situacao: str
    dataPagtoBaixa: Union[str, date]
    dataVencimento: Union[str, date]
    valorNominal: float
    valorTotalRecebimento: float
    email: str
    ddd: str
    telefone: str
    dataEmissao: Union[str, date]
    dataLimite: Union[str, date]
    linhaDigitavel: str
    desconto1: Desconto
    desconto2: Desconto
    desconto3: Desconto
    multa: Multa
    mora: Mora
    valorAbatimento: float

    def convert_date(self, field: str) -> None:
        value = getattr(self, field)
        if isinstance(value, str):
            setattr(self, field, str_to_date(value))

    def __post_init__(self):
        self.convert_date('dataPagtoBaixa')
        self.convert_date('dataVencimento')
        self.convert_date('dataEmissao')
        self.convert_date('dataLimite')


class SummaryContent(TypedDict):
    quantidade: int
    valor: float


class Summary(TypedDict):
    recebidos: SummaryContent
    previstos: SummaryContent
    baixados: SummaryContent
    expirados: SummaryContent


class ResponseList(TypedDict):
    totalPages: int
    totalElements: int
    numberOfElements: int
    last: bool
    first: bool
    size: int
    summary: Summary
    content: List[BoletoItem]


def get_lista_boletos(data_inicial: date, data_final: date,
                      configs: RequestConfigs,
                      filtrar: Optional[FiltrarEnum] = None,
                      ordernar: Optional[OrdenarEnum] = None,
                      page: Optional[int] = None, size: Optional[int] = None
                      ) -> ResponseList:
    """Recupera uma coleção de boletos por um período específico, de acordo 
    com os parametros informados.

    Está pesquisa retorna os boletos no padrão D+1, ou seja, os boletos 
    inseridos na data atual só serão visíveis a partir do dia seguinte.

    Parameters
    ----------
    data_inicial : date
        Data de início para o filtro.
    data_final : date
        Data de fim para o filtro.
    configs : RequestConfigs
        Dicionário de configuração com número de conta e certificados de 
        autenticação.
    filtrar : Optional[FiltrarEnum], optional
        Opção para situação atual do boleto, None caso não seja especificado.
    ordernar : Optional[OrdenarEnum], optional
        Opção de ordenação do retorno da consulta, None caso não seja 
        especificado.
    page : Optional[int], optional
        Número da página, None caso não seja especificado. Valor máximo: 20.
    size : Optional[int], optional
        Tamanho da página, None caso não seja especificado.

    Returns
    -------
    ResponseList
        Resultado da busca.
    """
    headers = {'x-inter-conta-corrente': strip_chars(configs['conta_inter'])}
    cert = str(check_file(configs['cert']))
    key = str(check_file(configs['key']))

    params = {
        'dataInicial': str(data_inicial),
        'dataFinal': str(data_final)
    }

    if filtrar is not None:
        params.update({'filtrarPor': filtrar.value})

    if ordernar is not None:
        params.update({'ordernarPor': ordernar.value})

    if size is not None:
        size = 20 if size > 20 else size
        params.update({'size': size})

    if page is not None:
        params.update({'page': page})

    response = get(_API_URL, params=params, headers=headers, cert=(cert, key))

    contents = check_response(response, "Filtragem inválida.")

    return ResponseList(**contents)
