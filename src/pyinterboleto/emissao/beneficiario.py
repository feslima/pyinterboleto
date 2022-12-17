from dataclasses import dataclass, fields
from typing import Union

from unidecode import unidecode

from ..common.tipo_pessoa import TipoPessoa
from ..utils.sanitize import sanitize_cep, sanitize_cnpj, sanitize_cpf


@dataclass
class Beneficiario:
    """Define a representação de um objeto beneficiário requerido pela API.

    Parameters
    ----------
    cpfCnpj : str
        CPF (FISICA) ou CNPJ (JURIDICA) da pessoa. Aceita pontuação ('.', '-' e
        '/'). Esta pontuação é removida na validação.

    tipoPessoa: Union[str, TipoPessoa]
        Tipo de pessoa: FISICA ou JURIDICA.

    nome: str
        Nome da pessoa.

        Acentos e demais caracteres são convertidos para ASCII na validação.

        Isto é para evitar conflitos com a API do Inter...

        Caracteres do tipo '&' também não devem ser usados.

    endereco : str
        Endereço da pessoa.

    bairro : str
        Bairro da pessoa.

    cidade : str
        Cidade da pessoa.

    uf : str
        UF da pessoa. (Sigla de dois caracteres do estado)

    cep : str
        CEP da pessoa. Aceita pontuação ('-'). Esta pontuação é removida na
        validação.

    Notes
    -----
    - Validações de tamanho máximo de strings são feita no __post_init__,
    assim como higienização de CPF/CNPJ e CEPS
    """

    cpfCnpj: str
    tipoPessoa: Union[str, TipoPessoa]
    nome: str
    endereco: str
    bairro: str
    cidade: str
    uf: str
    cep: str

    def __post_init__(self):
        self.tipoPessoa = TipoPessoa(self.tipoPessoa)

        if self.tipoPessoa == TipoPessoa.FISICA:
            self.cpfCnpj = sanitize_cpf(self.cpfCnpj)
            assert len(self.cpfCnpj) == 11
        else:
            self.cpfCnpj = sanitize_cnpj(self.cpfCnpj)
            assert len(self.cpfCnpj) == 14

        assert 1 <= len(self.nome) <= 100
        assert 1 <= len(self.endereco) <= 100
        assert 1 <= len(self.bairro) <= 60

        assert 1 <= len(self.cidade) <= 60
        assert len(self.uf) == 2

        self.cep = sanitize_cep(self.cep)
        assert len(self.cep) == 8

        # strip accents
        for field in fields(self):
            v = getattr(self, field.name)
            if isinstance(v, str):
                setattr(self, field.name, unidecode(v))
