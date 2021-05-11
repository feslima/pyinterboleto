from datetime import date
from io import BytesIO
from typing import Optional, Union, overload

from .baixa import CodigoBaixaEnum, executa_baixa
from .consulta.detalhado import BoletoDetail, get_boleto_detail
from .consulta.lista import (FiltrarEnum, OrdenarEnum, ResponseList,
                             get_lista_boletos)
from .consulta.pdf import get_pdf_boleto_in_memory, get_pdf_boleto_to_file
from .emissao.emissor import BoletoResponse, Emissao, emitir_boleto
from .utils.requests import PathType, RequestConfigs


class Boleto:
    """Objeto para consultas e emissão de boletos.

    Parameters
    ----------
    configs: RequestConfigs
        Dicionário de configuração com número de conta e certificados de 
        autenticação.

    Notes
    -----
    No caso de emissões, o método `emitir` só pode ser chamado caso a instância
    desta classe não tenha feito qualquer consulta detalhada (i.e. que tenha 
    chamado os métodos `consulta_detalhada` ou `consulta_pdf`) ou emissão 
    prévia. Isto é para evitar emissões com numerações repetidas e demais 
    conflitos.

    Ou seja, múltiplas consultas detalhadas com a mesma instância são 
    permitidas, e emissão só é permitida uma vez por instância e que não tenha 
    havido consultas detalhadas prévias.

    """

    def __init__(self, configs: RequestConfigs) -> None:
        self._configs = configs
        self._emitido: bool = False
        self._numero: str = ''

    def __str__(self) -> str:
        numero = self.numero if self.numero != '' else 'não tem'
        foi_emitido = 'sim' if self.emitido else 'não'
        emissivel = 'sim' if self.pode_emitir else 'não'
        string = (f"Número: {numero}\nFoi emitido: {foi_emitido}\n"
                  f"É emissivel: {emissivel}")

        return string

    @property
    def configs(self) -> RequestConfigs:
        return self._configs

    @property
    def emitido(self) -> bool:
        return self._emitido

    @property
    def pode_emitir(self) -> bool:
        return self._numero == '' and not self.emitido

    @property
    def numero(self) -> str:
        """Número de identificação do boleto na API.

        Se o boleto ainda não foi emitido, ou houve alguma consulta detalhada
        (`consulta_detalhada` ou `consulta_pdf`), essa propriedade é um string 
        vazio.
        """
        return self._numero

    def emitir(self, dados: Emissao) -> BoletoResponse:
        """Emite um boleto baseado nos `dados` provisionados.

        O boleto incluído estará disponível para consulta e pagamento, após 
        um tempo apróximado de 5 minutos da sua inclusão. Esse tempo é 
        necessário para o registro do boleto na CIP.

        Parameters
        ----------
        dados : Emissao
            Estrutura que representa o detalhamento dos dados necessários para 
            a emissão de um boleto.

        Returns
        -------
        BoletoResponse
            Dicionário que descreve o resultado de uma emissão de boleto bem 
            sucedida.

        Raises
        ------
        ValueError
            Caso esta instância já tenha emitido ou consultado detalhadamente 
            algum boleto.

        Examples
        --------
        >>> from pathlib import Path
        >>> from datetime import date, timedelta
        >>> from pprint import pprint
        >>> from pyinterboleto import Boleto, Emissao, Pagador, RequestConfigs
        >>> direc = Path('caminho/para/pasta/com/certificados')
        >>> cert = direc / 'Inter API_Certificado.crt'
        >>> key = direc / 'Inter API_Chave.key'
        >>> acc = '12345678'
        >>> configs = RequestConfigs(conta_inter=acc, certificate=cert, key=key)
        >>> boleto = Boleto(configs)
        >>> pagador = Pagador(
        ...     tipoPessoa='FISICA',
        ...     cnpjCpf='123.456.789-09',
        ...     nome="Pessoa Ficticia da Silva",
        ...     endereco="Rua Fantasia",
        ...     numero='300',
        ...     bairro='Centro',
        ...     cidade='São Paulo',
        ...     uf='SP',
        ...     cep='123456-789'
        ... )
        ... emissao = Emissao(
        ...     pagador=pagador, seuNumero='00001',
        ...     cnpjCPFBeneficiario='12.345.678/0001-01',
        ...     valorNominal=0.01,
        ...     dataEmissao=date.today(),
        ...     dataVencimento=date.today()+timedelta(days=2)
        ... )
        >>> result = boleto.emitir(emissao)
        >>> print(result)
        {'seuNumero': '00001', 'nossoNumero': '00123456789', 
         'codigoBarras': '00000000000000000000000000000000000000000000', 
         'linhaDigitavel': '00000000000000000000000000000000000000000000000'}

        """
        if not self.pode_emitir:
            raise ValueError("Este boleto já foi emitido.")

        result = emitir_boleto(dados, self.configs)
        self._emitido = True
        self._numero = result['nossoNumero']
        return result

    def consulta_detalhada(self, nosso_numero: str) -> BoletoDetail:
        """Recupera as informações de um boleto.

        Está pesquisa retorna as informações de um boleto no padrão D+0, ou 
        seja, as informações do boleto são consultadas diretamente na CIP 
        refletindo a situação em tempo real.

        Parameters
        ----------
        nosso_numero : str
            Número identificador do título.

        Returns
        -------
        BoletoDetail
            Dicionário de representação detalhada de um boleto.

        Notes
        -----
        Emissões não podem ser feitas após a chamada deste método.

        Examples
        --------
        >>> from pathlib import Path
        >>> from pprint import pprint
        >>> from pyinterboleto import Boleto, RequestConfigs
        >>> direc = Path('caminho/para/pasta/com/certificados')
        >>> cert = direc / 'Inter API_Certificado.crt'
        >>> key = direc / 'Inter API_Chave.key'
        >>> acc = '12345678'
        >>> configs = RequestConfigs(conta_inter=acc, certificate=cert, key=key)
        >>> boleto = Boleto(configs)
        >>> num_boleto = '00123456789'
        >>> detail = boleto.consulta_detalhada(num_boleto)
        >>> pprint(detail)
        {'cnpjCpfBeneficiario': '00000000000000',
         'cnpjCpfPagador': '12345678909',
         'codigoBarras': '00000000000000000000000000000000000000000000',
         'codigoEspecie': 'OUTROS',
         'dataEmissao': '01/05/2021',
         'dataHoraSituacao': '01/05/2021 15:22',
         'dataLimitePagamento': '11/06/2021',
         'dataVencimento': '12/05/2021',
         'dddPagador': '',
         'desconto1': Desconto(codigoDesconto=<CodigoDescontoEnum.NTD: 'NAOTEMDESCONTO'>, taxa=0.0, valor=0.0, data=''),
         'desconto2': Desconto(codigoDesconto=<CodigoDescontoEnum.NTD: 'NAOTEMDESCONTO'>, taxa=0.0, valor=0.0, data=''),
         'desconto3': Desconto(codigoDesconto=<CodigoDescontoEnum.NTD: 'NAOTEMDESCONTO'>, taxa=0.0, valor=0.0, data=''),
         'emailPagador': '',
         'linhaDigitavel': '00000000000000000000000000000000000000000000000',
         'mora': Mora(codigoMora=<CodigoMoraEnum.I: 'ISENTO'>, taxa=0.0, valor=0.0, data=''),
         'multa': Multa(codigoMulta=<CodigoMultaEnum.NTM: 'NAOTEMMULTA'>, taxa=0.0, valor=0.0, data=''),
         'nomeBeneficiario': 'NOME DO BENEFICIARIO CONTA PJ',
         'nomePagador': 'Pessoa Ficticia da Silva',
         'seuNumero': '00001',
         'situacao': 'EMABERTO',
         'telefonePagador': '',
         'tipoPessoaBeneficiario': 'JURIDICA',
         'tipoPessoaPagador': 'FISICA',
         'valorAbatimento': 0.0,
         'valorNominal': 0.01}

        """
        detail = get_boleto_detail(nosso_numero, self.configs)
        self._numero = nosso_numero
        return detail

    @overload
    def consulta_pdf(self, nosso_numero: str) -> BytesIO: ...

    @overload
    def consulta_pdf(self, nosso_numero: str, filename: PathType) -> None: ...

    def consulta_pdf(self, nosso_numero: str,
                     filename: Optional[PathType] = None) -> Optional[BytesIO]:
        """Captura o boleto em um buffer na memória ou em arquivo.

        Parameters
        ----------
        nosso_numero : str
            Número identificador do título.

        filename : Optional[PathType], optional
            Nome do arquivo a ser salvo. Caso seja especificado, salva o 
            conteúdo do buffer (BytesIO) no arquivo.

        Returns
        -------
        Optional[BytesIO]
            Objeto do tipo bytes se `filename` não for especificado (None). 
            Já é decodificado (base64) e pronto pra manuseio.

            Se `filename` for especificado (not None), não há retorno desta 
            função.

        Examples
        --------
        >>> from pathlib import Path
        >>> from pyinterboleto import Boleto, RequestConfigs
        >>> direc = Path('caminho/para/pasta/com/certificados')
        >>> cert = direc / 'Inter API_Certificado.crt'
        >>> key = direc / 'Inter API_Chave.key'
        >>> acc = '12345678'
        >>> configs = RequestConfigs(conta_inter=acc, certificate=cert, key=key)
        >>> boleto = Boleto(configs)
        >>> num_boleto = '00123456789'
        >>> pdf = boleto.consulta_pdf(num_boleto)
        >>> print(pdf)
        <_io.BytesIO object at 0x7fab0c068220>

        """
        pdf: Union[None, BytesIO]
        if filename is None:
            pdf = get_pdf_boleto_in_memory(nosso_numero, self.configs)
        else:
            pdf = get_pdf_boleto_to_file(nosso_numero, filename, self.configs)

        self._numero = nosso_numero
        return pdf

    def consulta_lista(self, data_inicial: date, data_final: date,
                       filtrar: Optional[FiltrarEnum] = None,
                       ordernar: Optional[OrdenarEnum] = None,
                       page: Optional[int] = None,
                       size: Optional[int] = None) -> ResponseList:
        """Recupera uma coleção de boletos por um período específico, de acordo 
        com os parametros informados.

        Está pesquisa retorna os boletos no padrão D+1, ou seja, os boletos 
        inseridos na data atual só serão visíveis a partir do dia seguinte.

        Parameters
        ----------
        data_inicial : date
            Data de início para o filtro. Esta data corresponde a data de 
            vencimento dos títulos. Isto é, a filtragem vai incluir títulos com
            data de vencimento A PARTIR desta data.

        data_final : date
            Data de fim para o filtro. Esta data corresponde a data de 
            vencimento dos títulos. Isto é, a filtragem vai incluir títulos com
            data de vencimento ATÉ esta data.

        filtrar : Optional[FiltrarEnum], optional
            Opção para situação atual do boleto, None caso não seja 
            especificado.

        ordernar : Optional[OrdenarEnum], optional
            Opção de ordenação do retorno da consulta, None caso não seja 
            especificado.

        page : Optional[int], optional
            Número da página, None caso não seja especificado. Valor máximo: 20.

        size : Optional[int], optional
            Tamanho da página, None caso não seja especificado.

        Returns
        -------
        ResponseList
            Resultado da busca.

        Examples
        --------
        >>> from pathlib import Path
        >>> from pprint import pprint
        >>> from datetime import date, timedelta
        >>> from pyinterboleto import Boleto, RequestConfigs
        >>> direc = Path('caminho/para/pasta/com/certificados')
        >>> cert = direc / 'Inter API_Certificado.crt'
        >>> key = direc / 'Inter API_Chave.key'
        >>> acc = '12345678'
        >>> configs = RequestConfigs(conta_inter=acc, certificate=cert, key=key)
        >>> boleto = Boleto(configs)
        >>> inicial = date.today() - timedelta(days=30)
        >>> final = date.today()
        >>> lista = boleto.consulta_lista(inicial, final)
        >>> pprint(lista)
        {'content': [{'cnpjCpfSacado': '12345678909',
            'dataEmissao': '09/01/2021',
            'dataLimite': '10/02/2021',
            'dataVencimento': '21/01/2021',
            'desconto1': {'codigo': 'NAOTEMDESCONTO',
                        'taxa': 0.0,
                        'valor': 0.0},
            'desconto2': {'codigo': 'NAOTEMDESCONTO',
                        'taxa': 0.0,
                        'valor': 0.0},
            'desconto3': {'codigo': 'NAOTEMDESCONTO',
                        'taxa': 0.0,
                        'valor': 0.0},
            'email': '',
            'linhaDigitavel': '00000000000000000000000000000000000000000000000',
            'mora': {'codigo': 'ISENTO', 'taxa': 0.0, 'valor': 0.0},
            'multa': {'codigo': 'NAOTEMMULTA', 'taxa': 0.0, 'valor': 0.0},
            'nomeSacado': 'Pessoa Ficticia da Silva',
            'nossoNumero': '00000000000',
            'seuNumero': '00001',
            'situacao': 'EMABERTO',
            'telefone': '',
            'valorAbatimento': 0.0,
            'valorJuros': 0.0,
            'valorMulta': 0.0,
            'valorNominal': 0.01}],
            'first': True,
            'last': True,
            'numberOfElements': 1,
            'size': 20,
            'summary': {'baixados': {'quantidade': 0, 'valor': 0},
                        'expirados': {'quantidade': 0, 'valor': 0},
                        'previstos': {'quantidade': 1, 'valor': 0.01},
                        'recebidos': {'quantidade': 0, 'valor': 0}},
            'totalElements': 1,
            'totalPages': 1}

        """
        lista = get_lista_boletos(data_inicial, data_final, self.configs,
                                  filtrar=filtrar, ordernar=ordernar,
                                  page=page, size=size)
        return lista

    def baixar_boleto(self, nosso_numero: str, codigo_baixa: CodigoBaixaEnum) \
            -> None:
        """Executa a baixa de um boleto.

        O registro da baixa é realizado no padrão D+1, ou seja, os boletos 
        baixados na data atual só serão baixados na base centralizada partir do 
        dia seguinte.

        Parameters
        ----------
        nosso_numero : str
            Número identificador do título.

        codigo_baixa : CodigoBaixaEnum
            Domínio que descreve o tipo de baixa sendo solicitado.

        Examples
        --------
        >>> from pathlib import Path
        >>> from pprint import pprint
        >>> from pyinterboleto import Boleto, RequestConfigs, CodigoBaixaEnum
        >>> direc = Path('caminho/para/pasta/com/certificados')
        >>> cert = direc / 'Inter API_Certificado.crt'
        >>> key = direc / 'Inter API_Chave.key'
        >>> acc = '12345678'
        >>> configs = RequestConfigs(conta_inter=acc, certificate=cert, key=key)
        >>> boleto = Boleto(configs)
        >>> num_boleto = '00123456789'
        >>> boleto.baixar_boleto(num_boleto, CodigoBaixaEnum.PC)

        """
        executa_baixa(nosso_numero, codigo_baixa, self.configs)
