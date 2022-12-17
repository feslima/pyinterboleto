from enum import Enum, unique


@unique
class TipoPessoa(Enum):
    FISICA = "FISICA"
    JURIDICA = "JURIDICA"
