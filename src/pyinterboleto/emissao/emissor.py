from dataclasses import asdict, dataclass, field
from datetime import date
from enum import Enum
from json import JSONEncoder, dumps
from typing import Any, Dict, Literal, Union

from ..utils.floats import is_non_zero_positive_float, is_positive_float
from ..utils.sanitize import sanitize_cnpj, sanitize_cpf, strip_chars
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
class Emissao:
    # mandatory attrs
    pagador: Pagador
    seuNumero: str
    cnpjCPFBeneficiario: str
    valorNominal: float
    dataEmissao: date
    dataVencimento: date
    numDiasAgenda: NUM_DIAS_AGENDA = field(default='TRINTA')
    desconto1: Desconto = field(default=SEM_DESCONTO_DICT)
    desconto2: Desconto = field(default=SEM_DESCONTO_DICT)
    desconto3: Desconto = field(default=SEM_DESCONTO_DICT)
    multa: Multa = field(default=SEM_MULTA)
    mora: Mora = field(default=SEM_MORA)

    # optional attrs
    valorAbatimento: float = 0.0
    mensagem: Mensagem = field(default=MENSAGEM_VAZIA)

    def __post_init__(self):
        assert len(self.seuNumero) <= 15

        self.cnpjCPFBeneficiario = strip_chars(self.cnpjCPFBeneficiario)
        if len(self.cnpjCPFBeneficiario) == 11:
            self.cnpjCPFBeneficiario = sanitize_cpf(self.cnpjCPFBeneficiario)
        else:
            self.cnpjCPFBeneficiario = sanitize_cnpj(self.cnpjCPFBeneficiario)

        assert len(self.cnpjCPFBeneficiario) == 14

        assert is_non_zero_positive_float(self.valorNominal)

        assert is_positive_float(self.valorAbatimento)

        assert self.dataVencimento >= self.dataEmissao

        if self.multa.codigoMulta != CodigoMultaEnum.NTM:
            assert self.multa.data > self.dataVencimento

        if self.mora.codigoMora != CodigoMoraEnum.I:
            assert self.mora.data > self.dataVencimento

    def to_dict(self) -> Dict[str, Union[str, float, SerializedDict]]:
        return asdict(self)

    def to_json(self) -> str:
        return dumps(self.to_dict(), cls=DefaultEncoder)
