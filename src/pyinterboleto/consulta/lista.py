from dataclasses import dataclass
from datetime import date
from enum import Enum, unique
from typing import List, Optional, Union

from dacite.core import from_dict
from requests import get
from tabulate import tabulate

from ..auth import get_api_configs
from ..common.desconto import DescontoConsulta
from ..common.mora import MoraConsulta
from ..common.multa import MultaConsulta
from ..utils.requests import RequestConfigs
from ..utils.sanitize import ConvertDateMixin, check_response
from ..utils.url import API_URL


@unique
class FiltrarEnum(Enum):
    """Enum para situação atual do boleto para filtro.

    - T: Todos os títulos do cliente no período;
    - V: Todos os títulos a vencer/vencidos do cliente no período;
    - E: Todos os títulos expirados (não passível de pagamento) no período;
    - P: Todos os títulos pagos em condições normais do cliente no período;
    - TB: Todas as demais baixas do cliente no período;
    """

    T = "TODOS"
    V = "VENCIDOSAVENCER"
    E = "EXPIRADOS"
    P = "PAGOS"
    TB = "TODOSBAIXADOS"


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

    NNA = "NOSSONUMERO"
    NND = "NOSSONUMERO_DSC"
    SN = "SEUNUMERO"
    DVA = "DATAVENCIMENTO"
    DVD = "DATAVENCIMENTO_DSC"
    NS = "NOMESACADO"
    VA = "VALOR"
    VD = "VALOR_DSC"
    SA = "STATUS"
    SD = "STATUS_DSC"


@dataclass
class BoletoItem(ConvertDateMixin):
    nossoNumero: str
    seuNumero: str
    cnpjCpfSacado: str
    nomeSacado: str
    situacao: str
    dataVencimento: Union[str, date]
    valorNominal: float
    email: str
    telefone: str
    dataEmissao: Union[str, date]
    dataLimite: Union[str, date]
    linhaDigitavel: str
    desconto1: DescontoConsulta
    desconto2: DescontoConsulta
    desconto3: DescontoConsulta
    multa: MultaConsulta
    mora: MoraConsulta
    valorAbatimento: float
    dataPagtoBaixa: Union[str, date] = ""
    valorTotalRecebimento: float = 0.0

    def __post_init__(self):
        self.convert_date("dataPagtoBaixa")
        self.convert_date("dataVencimento")
        self.convert_date("dataEmissao")
        self.convert_date("dataLimite")


@dataclass
class SummaryContent:
    quantidade: int
    valor: float


@dataclass
class Summary:
    recebidos: SummaryContent
    previstos: SummaryContent
    baixados: SummaryContent
    expirados: SummaryContent


@dataclass
class ResponseList:
    totalPages: int
    totalElements: int
    numberOfElements: int
    last: bool
    first: bool
    size: int
    summary: Summary
    content: List[BoletoItem]

    def __str__(self) -> str:
        """Tabulando o conteúdo como representação de objeto."""
        field_list = [
            "nossoNumero",
            "seuNumero",
            "cnpjCpfSacado",
            "nomeSacado",
            "situacao",
            "dataVencimento",
            "valorNominal",
            "dataEmissao",
            "dataLimite",
        ]
        rows = [
            tuple(getattr(item, field) for field in field_list) for item in self.content
        ]
        return tabulate(rows, headers=field_list)


def get_lista_boletos(
    data_inicial: date,
    data_final: date,
    configs: RequestConfigs,
    filtrar: Optional[FiltrarEnum] = None,
    ordenar: Optional[OrdenarEnum] = None,
    page: Optional[int] = None,
    size: Optional[int] = None,
) -> ResponseList:
    """Recupera uma coleção de boletos por um período específico, de acordo
    com os parametros informados.

    Está pesquisa retorna os boletos no padrão D+1, ou seja, os boletos
    inseridos na data atual só serão visíveis a partir do dia seguinte.

    Parameters
    ----------
    data_inicial : date
        Data de início para o filtro. Esta data corresponde a data de
        vencimento dos títulos. Isto é, a filtragem vai incluir títulos com
        data de vencimento a partir desta data.

    data_final : date
        Data de fim para o filtro. Esta data corresponde a data de vencimento
        dos títulos. Isto é, a filtragem vai incluir títulos com data de
        vencimento até esta data.

    configs : RequestConfigs
        Dicionário de configuração com número de conta e certificados de
        autenticação.

    filtrar : Optional[FiltrarEnum], optional
        Opção para situação atual do boleto, None caso não seja especificado.

    ordenar : Optional[OrdenarEnum], optional
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
    token, certificate, key = get_api_configs(configs)

    headers = {"Authorization": f"Bearer {token}"}

    params = {"dataInicial": str(data_inicial), "dataFinal": str(data_final)}

    if filtrar is not None:
        params.update({"filtrarPor": filtrar.value})

    if ordenar is not None:
        params.update({"ordenarPor": ordenar.value})

    if size is not None:
        size = 20 if size > 20 else size
        params.update({"size": str(size)})

    if page is not None:
        params.update({"page": page})

    response = get(API_URL, params=params, headers=headers, cert=(certificate, key))

    contents = check_response(response, "Filtragem inválida.")

    return from_dict(ResponseList, contents)
