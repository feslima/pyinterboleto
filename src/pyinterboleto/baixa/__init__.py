from enum import Enum, unique


@unique
class CodigoBaixaEnum(Enum):
    """Domínio que descreve o tipo de baixa sendo solicitado.

    - A: Baixa por acertos;
    - P: Baixado por ter sido protestado;
    - D: Baixado para devolução;
    - PAB: Baixado por protesto após baixa;
    - PDC: Baixado, pago direto ao cliente;
    - S: Baixado por substituição;
    - FS: Baixado por falta de solução;
    - PC: Baixado a pedido do cliente;
    """
    A = 'ACERTOS'
    P = 'PROTESTADO'
    D = 'DEVOLUCAO'
    PAB = 'PROTESTOAPOSBAIXA'
    PDC = 'PAGODIRETOAOCLIENTE'
    S = 'SUBISTITUICAO'
    FS = 'FALTADESOLUCAO'
    PC = 'APEDIDODOCLIENTE'
