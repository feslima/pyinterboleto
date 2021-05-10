from dataclasses import dataclass


@dataclass
class Mensagem:
    """A mensagem que é mostrada no canhoto do boleto.

    Use para notificar o pagador de multas, juros, prazos, etc.

    Todas as linhas são vazias por padrão.
    """
    linha1: str = ''
    linha2: str = ''
    linha3: str = ''
    linha4: str = ''
    linha5: str = ''

    def __post_init__(self):
        assert len(self.linha1) <= 78
        assert len(self.linha2) <= 78
        assert len(self.linha3) <= 78
        assert len(self.linha4) <= 78
        assert len(self.linha5) <= 78


MENSAGEM_VAZIA = Mensagem()
