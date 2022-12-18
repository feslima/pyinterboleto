from dataclasses import dataclass
from datetime import date
from enum import Enum, unique
from typing import Union

from ..utils.floats import is_non_zero_positive_float, is_zero_float


@unique
class CodigoDescontoEnum(Enum):
    """Códigos de Desconto do Título.

    - NAO_TEM_DESCONTO -> Não tem desconto;
    - VALOR_FIXO_DATA_INFORMADA -> Valor fixo até data informada;
    - PERCENTUAL_DATA_INFORMADA -> Percentual até data informada;
    """

    NAO_TEM_DESCONTO = "NAOTEMDESCONTO"
    VALOR_FIXO_DATA_INFORMADA = "VALORFIXODATAINFORMADA"
    PERCENTUAL_DATA_INFORMADA = "PERCENTUALDATAINFORMADA"


@dataclass
class DescontoConsulta:
    """Representação de desconto usado em consultas.

    Parameters
    ----------
    codigo: Union[str, CodigoDescontoEnum]
        Código de desconto do título.

    data : Union[date, str], optional
        Data de desconto do título, string vazio ('') por valor padrão.

    taxa : float, optional
        Taxa percentual de desconto do título, valor padrão 0.0.

    valor : float, optional
        Valor de desconto, expresso na moeda do título, valor padrão 0.0.


    Notes
    -----

    Contém as seguintes validações:
    - data:
        1. Obrigatório para códigos de desconto (veja `CodigoDescontoEnum`)
        `VALOR_FIXO_DATA_INFORMADA` e `PERCENTUAL_DATA_INFORMADA`;
        2. Deve ser vazio ('') para código `NAO_TEM_DESCONTO`;
        3. Não informar ('') para os demais códigos;

    - taxa:
        1. Obrigatório para códigos de desconto `PERCENTUAL_DATA_INFORMADA`;
        2. Deve ser 0 para código `NAO_TEM_DESCONTO`;

    - valor:
        1. Obrigatório para códigos de desconto `VALOR_FIXO_DATA_INFORMADA`;
        2. Deve ser 0 para código `NAO_TEM_DESCONTO`;
    """

    codigo: Union[str, CodigoDescontoEnum]
    taxa: float = 0.0
    valor: float = 0.0
    data: Union[date, str] = ""

    def __post_init__(self):
        self.codigo = CodigoDescontoEnum(self.codigo)
        if self.codigo == CodigoDescontoEnum.NAO_TEM_DESCONTO:
            assert self.data == ""
            assert is_zero_float(self.taxa)
            assert is_zero_float(self.valor)

        else:
            if (
                self.codigo == CodigoDescontoEnum.VALOR_FIXO_DATA_INFORMADA
                or self.codigo == CodigoDescontoEnum.PERCENTUAL_DATA_INFORMADA
            ):
                assert isinstance(self.data, date)
            else:
                # não informar para os demais
                assert self.data == ""

            if self.codigo == CodigoDescontoEnum.PERCENTUAL_DATA_INFORMADA:
                assert is_non_zero_positive_float(self.taxa)

            if self.codigo == CodigoDescontoEnum.VALOR_FIXO_DATA_INFORMADA:
                assert is_non_zero_positive_float(self.valor)


@dataclass
class DescontoEmissao:
    """Representação de desconto usado em emissões.

    Parameters
    ----------
    codigoDesconto: Union[str, CodigoDescontoEnum]
        Código de desconto do título.

    data : Union[date, str], optional
        Data de desconto do título, string vazio ('') por valor padrão.

    taxa : float, optional
        Taxa percentual de desconto do título, valor padrão 0.0.

    valor : float, optional
        Valor de desconto, expresso na moeda do título, valor padrão 0.0.


    Notes
    -----

    Contém as seguintes validações:
    - data:
        1. Obrigatório para códigos de desconto (veja `CodigoDescontoEnum`)
        `VALOR_FIXO_DATA_INFORMADA` e `PERCENTUAL_DATA_INFORMADA`;
        2. Deve ser vazio ('') para código `NAO_TEM_DESCONTO`;
        3. Não informar ('') para os demais códigos;

    - taxa:
        1. Obrigatório para códigos de desconto `PERCENTUAL_DATA_INFORMADA`;
        2. Deve ser 0 para código `NAO_TEM_DESCONTO`;

    - valor:
        1. Obrigatório para códigos de desconto `VALOR_FIXO_DATA_INFORMADA`;
        2. Deve ser 0 para código `NAO_TEM_DESCONTO`;
    """

    codigoDesconto: Union[str, CodigoDescontoEnum]
    taxa: float = 0.0
    valor: float = 0.0
    data: Union[date, str] = ""

    def __post_init__(self):
        self.codigoDesconto = CodigoDescontoEnum(self.codigoDesconto)
        if self.codigoDesconto == CodigoDescontoEnum.NAO_TEM_DESCONTO:
            assert self.data == ""
            assert is_zero_float(self.taxa)
            assert is_zero_float(self.valor)

        else:
            if (
                self.codigoDesconto == CodigoDescontoEnum.VALOR_FIXO_DATA_INFORMADA
                or self.codigoDesconto == CodigoDescontoEnum.PERCENTUAL_DATA_INFORMADA
            ):
                assert isinstance(self.data, date)
            else:
                # não informar para os demais
                assert self.data == ""

            if self.codigoDesconto == CodigoDescontoEnum.PERCENTUAL_DATA_INFORMADA:
                assert is_non_zero_positive_float(self.taxa)

            if self.codigoDesconto == CodigoDescontoEnum.VALOR_FIXO_DATA_INFORMADA:
                assert is_non_zero_positive_float(self.valor)
