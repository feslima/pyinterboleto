from dataclasses import dataclass
from datetime import date
from enum import Enum, unique
from typing import Union

from ..utils.floats import is_non_zero_positive_float, is_zero_float


@unique
class CodigoDescontoEnum(Enum):
    """Códigos de Desconto do Título.

    - NTD -> Não tem desconto;
    - VFDI -> Valor fixo até data informada;
    - PDI -> Percentual até data informada;
    - VADC -> Valor por atencipação (dia corrido);
    - VADU -> Valor por atencipação (dia útil);
    - PVNDC -> Percentual sobre valor nominal por dia corrido;
    - PVNDU -> Percentual sobre valor nominal por dia útil;
    """

    NTD = 'NAOTEMDESCONTO'
    VFDI = 'VALORFIXODATAINFORMADA'
    VADC = 'VALORANTECIPACAODIACORRIDO'
    VADU = 'VALORANTECIPACAODIAUTIL'
    PDI = 'PERCENTUALDATAINFORMADA'
    PVNDC = 'PERCENTUALVALORNOMINALDIACORRIDO'
    PVNDU = 'PERCENTUALVALORNOMINALDIAUTIL'

    @classmethod
    def percentuais(cls):
        return tuple(i for i in cls if i.name.startswith('P'))

    @classmethod
    def valores(cls):
        return tuple(i for i in cls if i.name.startswith('V'))


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
        `VFDI` e `PDI`;
        2. Deve ser vazio ('') para código `NTD`;
        3. Não informar ('') para os demais códigos;

    - taxa:
        1. Obrigatório para códigos de desconto `PDI`, `PVNDC` e `PVNDU`;
        2. Deve ser 0 para código `NTD`;

    - valor:
        1. Obrigatório para códigos de desconto `VFDI`, `VADC` e `VADU`;
        2. Deve ser 0 para código `NTD`;
    """
    codigo: Union[str, CodigoDescontoEnum]
    taxa: float = 0.0
    valor: float = 0.0
    data: Union[date, str] = ""

    def __post_init__(self):
        self.codigo = CodigoDescontoEnum(self.codigo)
        if self.codigo == CodigoDescontoEnum.NTD:
            assert self.data == ""
            assert is_zero_float(self.taxa)
            assert is_zero_float(self.valor)

        else:
            if self.codigo == CodigoDescontoEnum.VFDI or \
                    self.codigo == CodigoDescontoEnum.PDI:
                assert isinstance(self.data, date)
            else:
                # não informar para os demais
                assert self.data == ""

            if self.codigo in CodigoDescontoEnum.percentuais():
                assert is_non_zero_positive_float(self.taxa)

            if self.codigo in CodigoDescontoEnum.valores():
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
        `VFDI` e `PDI`;
        2. Deve ser vazio ('') para código `NTD`;
        3. Não informar ('') para os demais códigos;

    - taxa:
        1. Obrigatório para códigos de desconto `PDI`, `PVNDC` e `PVNDU`;
        2. Deve ser 0 para código `NTD`;

    - valor:
        1. Obrigatório para códigos de desconto `VFDI`, `VADC` e `VADU`;
        2. Deve ser 0 para código `NTD`;
    """
    codigoDesconto: Union[str, CodigoDescontoEnum]
    taxa: float = 0.0
    valor: float = 0.0
    data: Union[date, str] = ""

    def __post_init__(self):
        self.codigoDesconto = CodigoDescontoEnum(self.codigoDesconto)
        if self.codigoDesconto == CodigoDescontoEnum.NTD:
            assert self.data == ""
            assert is_zero_float(self.taxa)
            assert is_zero_float(self.valor)

        else:
            if self.codigoDesconto == CodigoDescontoEnum.VFDI or \
                    self.codigoDesconto == CodigoDescontoEnum.PDI:
                assert isinstance(self.data, date)
            else:
                # não informar para os demais
                assert self.data == ""

            if self.codigoDesconto in CodigoDescontoEnum.percentuais():
                assert is_non_zero_positive_float(self.taxa)

            if self.codigoDesconto in CodigoDescontoEnum.valores():
                assert is_non_zero_positive_float(self.valor)
