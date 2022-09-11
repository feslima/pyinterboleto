from dataclasses import dataclass
from datetime import date
from enum import Enum, unique
from typing import Union

from ..utils.floats import is_non_zero_positive_float, is_zero_float
from ..utils.sanitize import ConvertDateMixin


@unique
class CodigoMultaEnum(Enum):
    """Código de multa título.

    - NTM -> Não tem multa;
    - VF -> Valor fixo;
    - P -> Percentual;
    """

    NTM = "NAOTEMMULTA"
    VF = "VALORFIXO"
    P = "PERCENTUAL"


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
        1. Obrigatório para códigos de multa (veja `CodigoMultaEnum`) `VF` e
        `P`;
        2. Deve ser vazio ('') para código `NTM`;
        3. Não informar ('') para os demais códigos;
        4. Deve ser maior que vencimento e marca data de início de cobrança de
        multa (incluindo essa data) [Essa validação é feita na classe mãe que
        usa esta classe];

    - taxa:
        1. Obrigatório para código de multa `P`;
        2. Deve ser 0 para código `NTM`;

    - valor:
        1. Obrigatório para código de multa `VF`;
        2. Deve ser 0 para código `NTM`;
    """

    codigo: Union[str, CodigoMultaEnum]
    taxa: float = 0.0
    valor: float = 0.0
    data: Union[date, str] = ""

    def __post_init__(self):
        self.codigo = CodigoMultaEnum(self.codigo)

        if self.codigo == CodigoMultaEnum.NTM:
            assert self.data == ""
            assert is_zero_float(self.taxa)
            assert is_zero_float(self.valor)

        else:
            self.convert_date("data")

            if self.codigo == CodigoMultaEnum.VF:
                assert is_non_zero_positive_float(self.valor)

            if self.codigo == CodigoMultaEnum.P:
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
        1. Obrigatório para códigos de multa (veja `CodigoMultaEnum`) `VF` e
        `P`;
        2. Deve ser vazio ('') para código `NTM`;
        3. Não informar ('') para os demais códigos;
        4. Deve ser maior que vencimento e marca data de início de cobrança de
        multa (incluindo essa data) [Essa validação é feita na classe mãe que
        usa esta classe];

    - taxa:
        1. Obrigatório para código de multa `P`;
        2. Deve ser 0 para código `NTM`;

    - valor:
        1. Obrigatório para código de multa `VF`;
        2. Deve ser 0 para código `NTM`;
    """

    codigoMulta: Union[str, CodigoMultaEnum]
    taxa: float = 0.0
    valor: float = 0.0
    data: Union[date, str] = ""

    def __post_init__(self):
        self.codigoMulta = CodigoMultaEnum(self.codigoMulta)

        if self.codigoMulta == CodigoMultaEnum.NTM:
            assert self.data == ""
            assert is_zero_float(self.taxa)
            assert is_zero_float(self.valor)

        else:
            self.convert_date("data")

            if self.codigoMulta == CodigoMultaEnum.VF:
                assert is_non_zero_positive_float(self.valor)

            if self.codigoMulta == CodigoMultaEnum.P:
                assert is_non_zero_positive_float(self.taxa)
