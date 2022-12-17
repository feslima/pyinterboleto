from dataclasses import dataclass
from datetime import date
from enum import Enum, unique
from typing import Iterable, List, Literal, Optional

from dacite.core import from_dict
from requests import get
from tabulate import tabulate

from ..auth import get_api_configs
from ..utils.requests import RequestConfigs
from ..utils.sanitize import check_response
from ..utils.url import API_URL
from .detalhado import BoletoDetail


@unique
class FiltrarDataPorEnum(str, Enum):
    """Os filtros de data inicial e data final se aplicarão a:

    VENCIMENTO - Filtro de data pelo vencimento.
    EMISSAO - Filtro de data pela emissão.
    SITUACAO - Filtro de data pela mudança de situação.

    Caso o campo situacao seja:
    - EXPIRADO as datas corresponderão a data de expiração dos boletos;
    - VENCIDO as datas corresponderão a data de vencimento dos boletos;
    - EMABERTO as datas corresponderão a data de emissão dos boletos;
    - PAGO as datas corresponderão a data de pagamento dos boletos;
    - CANCELADO as datas corresponderão a data de cancelamento dos boletos;
    """

    VENCIMENTO = "VENCIMENTO"
    EMISSAO = "EMISSAO"
    SITUACAO = "SITUACAO"


@unique
class SituacaoEnum(str, Enum):
    """Filtro pela situação da cobrança.

    EXPIRADO
    VENCIDO
    EMABERTO
    PAGO
    CANCELADO
    """

    EXPIRADO = "EXPIRADO"
    VENCIDO = "VENCIDO"
    EMABERTO = "EMABERTO"
    PAGO = "PAGO"
    CANCELADO = "CANCELADO"


@unique
class OrdenarEnum(str, Enum):
    """Enum para ordenação do retorno da consulta.

    - PAGADOR
    - NOSSONUMERO
    - SEUNUMERO
    - DATASITUACAO
    - DATAVENCIMENTO
    - VALOR
    - STATUS
    """

    PAGADOR = "PAGADOR"
    NOSSONUMERO = "NOSSONUMERO"
    SEUNUMERO = "SEUNUMERO"
    DATASITUACAO = "DATASITUACAO"
    DATAVENCIMENTO = "DATAVENCIMENTO"
    VALOR = "VALOR"
    STATUS = "STATUS"


@dataclass
class ResponseList:
    totalPages: int
    totalElements: int
    numberOfElements: int
    last: bool
    first: bool
    size: int
    content: List[BoletoDetail]

    def __str__(self) -> str:
        """Tabulando o conteúdo como representação de objeto."""
        field_list = [
            "nossoNumero",
            "seuNumero",
            "cnpjCpfBeneficiario",
            "nomeBeneficiario",
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
    token: str,
    configs: RequestConfigs,
    data_inicial: date,
    data_final: date,
    filtrar_data_por: FiltrarDataPorEnum = FiltrarDataPorEnum.VENCIMENTO,
    situacao: Optional[Iterable[SituacaoEnum]] = None,
    nome: Optional[str] = None,
    email: Optional[str] = None,
    cpf_cnpj: Optional[str] = None,
    itens_por_pagina: int = 100,
    pagina_atual: int = 0,
    ordenar: OrdenarEnum = OrdenarEnum.PAGADOR,
    tipo_ordenacao: Literal["ASC", "DESC"] = "ASC",
) -> ResponseList:
    """Recupera uma coleção de boletos por um período específico, de acordo
    com os parametros informados.

    Está pesquisa retorna os boletos no padrão D+1, ou seja, os boletos
    inseridos na data atual só serão visíveis a partir do dia seguinte.

    Parameters
    ----------
    token : str
        Token de autenticação da API do Banco Inter. Veja:
        https://developers.bancointer.com.br/reference/obtertoken

    configs : RequestConfigs
        Dicionário de configuração com número de conta e certificados de
        autenticação.

    data_inicial : date
        Data de início para o filtro. Esta data corresponde a data de
        vencimento dos títulos. Isto é, a filtragem vai incluir títulos com
        data de vencimento a partir desta data.

    data_final : date
        Data de fim para o filtro. Esta data corresponde a data de vencimento
        dos títulos. Isto é, a filtragem vai incluir títulos com data de
        vencimento até esta data.

    filtrar_data_por : FiltrarDataPorEnum, optional
        Veja documentação do enum FiltrarDataPorEnum, VENCIMENTO caso não seja
        especificado.

    situacao : Optional[Iterable[SituacaoEnum]], optional
        Filtro pela situação da cobrança. Aceita multiplos valores, None caso não
        seja especificado.

    nome : Optional[str], optional
        Filtro pelo nome do pagador, None caso não seja especificado.

    email : Optional[str], optional
        Filtro pelo email do pagador, None caso não seja especificado.

    cpf_cnpj : Optional[str], optional
        Filtro pelo CPF ou CNPJ do pagador, None caso não seja especificado.

    ordenar : OrdenarEnum, optional
        Opção de ordenação do retorno da consulta, PAGADOR caso não seja
        especificado.

    itens_por_pagina : int, optional
        Quantidade máxima de registros retornados em cada página. Apenas a última
        página pode conter uma quantidade menor de registros, 100 itens caso não
        seja especificado.

        Valor mínimo: 1
        Valor máximo: 1000

    pagina_atual : int, optional
        Página a ser retornada pela consulta. Se não informada, assumirá que será 0.

    tipo_ordenacao : 'ASC' | 'DESC', optional
        Opção para tipo de ordenação, 'ASC' caso não seja especificado.

    Returns
    -------
    ResponseList
        Resultado da busca.
    """
    certificate, key = get_api_configs(configs)

    headers = {"Authorization": f"Bearer {token}"}

    itens_por_pagina = 1 if itens_por_pagina < 1 else itens_por_pagina
    itens_por_pagina = 1000 if itens_por_pagina > 1000 else itens_por_pagina

    params = {
        "dataInicial": str(data_inicial),
        "dataFinal": str(data_final),
        "ordenarPor": ordenar.value,
        "filtrarDataPor": filtrar_data_por.value,
        "tipoOrdenacao": tipo_ordenacao,
        "itensPorPagina": str(itens_por_pagina),
        "paginaAtual": pagina_atual,
    }

    if situacao is not None:
        params.update({"situacao": ",".join(s.value for s in situacao)})

    if nome is not None:
        params.update({"nome": nome})

    if email is not None:
        params.update({"email": email})

    if cpf_cnpj is not None:
        params.update({"cpfCnpj": cpf_cnpj})

    response = get(API_URL, params=params, headers=headers, cert=(certificate, key))

    contents = check_response(response, "Filtragem inválida.")

    return from_dict(ResponseList, contents)
