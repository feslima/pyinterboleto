from dataclasses import dataclass
from datetime import date
from enum import Enum, unique
from typing import Union

from ..utils.floats import is_non_zero_positive_float, is_zero_float
from ..utils.sanitize import ConvertDateMixin


@unique
class CodigoMoraEnum(Enum):
    """Código de mora do título

    - VD -> Valor ao dia;
    - TM -> Taxa mensal;
    - I -> Não há mora;
    """
    VD = 'VALORDIA'
    TM = 'TAXAMENSAL'
    I = 'ISENTO'


@dataclass
class MoraConsulta:
    """Representação de mora usado em consultas.

    Parameters
    ----------
    codigo: Union[str, CodigoMoraEnum]
        Código de mora do título.

    data : Union[date, str], optional
        Data de mora do título, string vazio ('') por valor padrão.

    taxa : float, optional
        Taxa percentual de mora do título, valor padrão 0.0.

    valor : float, optional
        Valor de mora, expresso na moeda do título, valor padrão 0.0.


    Notes
    -----

    Contém as seguintes validações:
    - data:    
        1. Obrigatório para códigos de mora (veja `CodigoMoraEnum`) `VD` e 
        `TM`;
        2. Deve ser vazio ('') para código `I`;
        3. Não informar ('') para os demais códigos;
        4. Deve ser maior que vencimento e marca data de início de cobrança de
        mora (incluindo essa data) [Essa validação é feita na classe mãe que
        usa esta classe];

    - taxa:
        1. Obrigatório para código de mora `TM`;
        2. Deve ser 0 para código `I`;

    - valor:
        1. Obrigatório para código de mora `VD`;
        2. Deve ser 0 para código `NTM`;
    """
    codigo: Union[str, CodigoMoraEnum]
    taxa: float = 0.0
    valor: float = 0.0
    data: Union[date, str] = ""

    def __post_init__(self):
        self.codigo = CodigoMoraEnum(self.codigo)

        if self.codigo == CodigoMoraEnum.I:
            assert self.data == ""
            assert is_zero_float(self.taxa)
            assert is_zero_float(self.valor)

        else:
            self.convert_date('data')

            if self.codigo == CodigoMoraEnum.VD:
                assert is_non_zero_positive_float(self.valor)

            if self.codigo == CodigoMoraEnum.TM:
                assert is_non_zero_positive_float(self.taxa)


@dataclass
class MoraEmissao:
    """Representação de mora usado em emissões.

    Parameters
    ----------
    codigoMora: Union[str, CodigoMoraEnum]
        Código de mora do título.

    data : Union[date, str], optional
        Data de mora do título, string vazio ('') por valor padrão.

    taxa : float, optional
        Taxa percentual de mora do título, valor padrão 0.0.

    valor : float, optional
        Valor de mora, expresso na moeda do título, valor padrão 0.0.


    Notes
    -----

    Contém as seguintes validações:
    - data:    
        1. Obrigatório para códigos de mora (veja `CodigoMoraEnum`) `VD` e 
        `TM`;
        2. Deve ser vazio ('') para código `I`;
        3. Não informar ('') para os demais códigos;
        4. Deve ser maior que vencimento e marca data de início de cobrança de
        mora (incluindo essa data) [Essa validação é feita na classe mãe que
        usa esta classe];

    - taxa:
        1. Obrigatório para código de mora `TM`;
        2. Deve ser 0 para código `I`;

    - valor:
        1. Obrigatório para código de mora `VD`;
        2. Deve ser 0 para código `NTM`;
    """
    codigoMora: Union[str, CodigoMoraEnum]
    taxa: float = 0.0
    valor: float = 0.0
    data: Union[date, str] = ""

    def __post_init__(self):
        self.codigoMora = CodigoMoraEnum(self.codigoMora)

        if self.codigoMora == CodigoMoraEnum.I:
            assert self.data == ""
            assert is_zero_float(self.taxa)
            assert is_zero_float(self.valor)

        else:
            self.convert_date('data')

            if self.codigoMora == CodigoMoraEnum.VD:
                assert is_non_zero_positive_float(self.valor)

            if self.codigoMora == CodigoMoraEnum.TM:
                assert is_non_zero_positive_float(self.taxa)
