from dataclasses import dataclass
from datetime import date
from enum import Enum, unique
from typing import Union

from ..utils.floats import is_non_zero_positive_float, is_zero_float
from ..utils.sanitize import ConvertDateMixin


@unique
class CodigoMultaEnum(Enum):
    """Código de multa título.

    - NAO_TEM_MULTA -> Não tem multa;
    - VALOR_FIXO -> Valor fixo;
    - PERCENTUAL -> Percentual;
    """

    NAO_TEM_MULTA = "NAOTEMMULTA"
    VALOR_FIXO = "VALORFIXO"
    PERCENTUAL = "PERCENTUAL"


@dataclass
class MultaConsulta(ConvertDateMixin):
    """Representação de multa usado em consultas.

    Parameters
    ----------
    codigo: Union[str, CodigoMultaEnum]
        Código de multa do título.

    data : Union[date, str], optional
        Data de multa do título, string vazio ('') por valor padrão.

    taxa : float, optional
        Taxa percentual de multa do título, valor padrão 0.0.

    valor : float, optional
        Valor de multa, expresso na moeda do título, valor padrão 0.0.


    Notes
    -----

    Contém as seguintes validações:
    - data:
        1. Obrigatório para códigos de multa (veja `CodigoMultaEnum`) `VALOR_FIXO` e
        `PERCENTUAL`;
        2. Deve ser vazio ('') para código `NAO_TEM_MULTA`;
        3. Não informar ('') para os demais códigos;
        4. Deve ser maior que vencimento e marca data de início de cobrança de
        multa (incluindo essa data) [Essa validação é feita na classe mãe que
        usa esta classe];

    - taxa:
        1. Obrigatório para código de multa `PERCENTUAL`;
        2. Deve ser 0 para código `NAO_TEM_MULTA`;

    - valor:
        1. Obrigatório para código de multa `VALOR_FIXO`;
        2. Deve ser 0 para código `NAO_TEM_MULTA`;
    """

    codigo: Union[str, CodigoMultaEnum]
    taxa: float = 0.0
    valor: float = 0.0
    data: Union[date, str] = ""

    def __post_init__(self):
        self.codigo = CodigoMultaEnum(self.codigo)

        if self.codigo == CodigoMultaEnum.NAO_TEM_MULTA:
            assert self.data == ""
            assert is_zero_float(self.taxa)
            assert is_zero_float(self.valor)

        else:
            self.convert_date("data")

            if self.codigo == CodigoMultaEnum.VALOR_FIXO:
                assert is_non_zero_positive_float(self.valor)

            if self.codigo == CodigoMultaEnum.PERCENTUAL:
                assert is_non_zero_positive_float(self.taxa)


@dataclass
class MultaEmissao(ConvertDateMixin):
    """Representação de multa usado em emissões.

    Parameters
    ----------
    codigoMulta: Union[str, CodigoMultaEnum]
        Código de multa do título.

    data : Union[date, str], optional
        Data de multa do título, string vazio ('') por valor padrão.

    taxa : float, optional
        Taxa percentual de multa do título, valor padrão 0.0.

    valor : float, optional
        Valor de multa, expresso na moeda do título, valor padrão 0.0.


    Notes
    -----

    Contém as seguintes validações:
    - data:
        1. Obrigatório para códigos de multa (veja `CodigoMultaEnum`) `VALOR_FIXO` e
        `PERCENTUAL`;
        2. Deve ser vazio ('') para código `NAO_TEM_MULTA`;
        3. Não informar ('') para os demais códigos;
        4. Deve ser maior que vencimento e marca data de início de cobrança de
        multa (incluindo essa data) [Essa validação é feita na classe mãe que
        usa esta classe];

    - taxa:
        1. Obrigatório para código de multa `PERCENTUAL`;
        2. Deve ser 0 para código `NAO_TEM_MULTA`;

    - valor:
        1. Obrigatório para código de multa `VALOR_FIXO`;
        2. Deve ser 0 para código `NAO_TEM_MULTA`;
    """

    codigoMulta: Union[str, CodigoMultaEnum]
    taxa: float = 0.0
    valor: float = 0.0
    data: Union[date, str] = ""

    def __post_init__(self):
        self.codigoMulta = CodigoMultaEnum(self.codigoMulta)

        if self.codigoMulta == CodigoMultaEnum.NAO_TEM_MULTA:
            assert self.data == ""
            assert is_zero_float(self.taxa)
            assert is_zero_float(self.valor)

        else:
            self.convert_date("data")

            if self.codigoMulta == CodigoMultaEnum.VALOR_FIXO:
                assert is_non_zero_positive_float(self.valor)

            if self.codigoMulta == CodigoMultaEnum.PERCENTUAL:
                assert is_non_zero_positive_float(self.taxa)
