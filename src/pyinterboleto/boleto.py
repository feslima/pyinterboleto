from datetime import date
from io import BytesIO
from typing import Iterable, Literal, Optional, Union, overload

from .auth import get_auth_token
from .baixa import CodigoBaixaEnum, executa_baixa
from .consulta.detalhado import BoletoDetail, get_boleto_detail
from .consulta.lista import (
    FiltrarDataPorEnum,
    OrdenarEnum,
    ResponseList,
    SituacaoEnum,
    get_lista_boletos,
)
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
        self._numero: str = ""
        self._auth_token: str = ""

    def __str__(self) -> str:
        numero = self.numero if self.numero != "" else "não tem"
        foi_emitido = "sim" if self.emitido else "não"
        emissivel = "sim" if self.pode_emitir else "não"
        string = (
            f"Número: {numero}\nFoi emitido: {foi_emitido}\n"
            f"É emissivel: {emissivel}"
        )

        return string

    @property
    def auth_token(self) -> str:
        """Token de autenticação utilizado nas operações relacionadas a boletos.
        Se a requisição de obtenção de token ainda não foi chamada (e.g. esta
        classe foi instanciada mas não teve nenhuma operação realizada) uma
        requisição de authenticação será feita."""
        if getattr(self, "_auth_token", "") == "":
            self._auth_token = get_auth_token(self.configs)

        return self._auth_token

    @property
    def configs(self) -> RequestConfigs:
        return self._configs

    @property
    def emitido(self) -> bool:
        return self._emitido

    @property
    def pode_emitir(self) -> bool:
        return self._numero == "" and not self.emitido

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
        >>> from pyinterboleto import Boleto, Emissao, Pagador, RequestConfigs, ScopeEnum
        >>> direc = Path('caminho/para/pasta/com/certificados')
        >>> cert = direc / 'Inter API_Certificado.crt'
        >>> key = direc / 'Inter API_Chave.key'
        >>> # client_id e client_secret são obtidos de acordo com a documentação do Inter
        >>> client_id = 'valor-do-id-uuid'
        >>> client_secret = 'valor-do-secret-uuid'
        >>> scopes = (ScopeEnum.EXTRATO_READ, ScopeEnum.BOLETO_COBRANCA_READ)
        >>> configs = RequestConfigs(client_id=client_id, client_secret=client_secret, scopes=scopes, certificate=cert, key=key)
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
        self._numero = result["nossoNumero"]
        return result

    def consulta_detalhada(self, nosso_numero: str) -> BoletoDetail:
        """Recupera as informações de um boleto.

        Está pesquisa retorna as informações de um boleto no padrão D+0, ou
        seja, as informações do boleto são consultadas diretamente na CIP
        refletindo a situação em tempo real.

        Escopo requerido: ScopeEnum.BOLETO_COBRANCA_READ

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
        >>> from pyinterboleto import Boleto, RequestConfigs, ScopeEnum
        >>> direc = Path('caminho/para/pasta/com/certificados')
        >>> cert = direc / 'Inter API_Certificado.crt'
        >>> key = direc / 'Inter API_Chave.key'
        >>> # client_id e client_secret são obtidos de acordo com a documentação do Inter
        >>> client_id = 'valor-do-id-uuid'
        >>> client_secret = 'valor-do-secret-uuid'
        >>> scopes = (ScopeEnum.BOLETO_COBRANCA_READ,)
        >>> configs = RequestConfigs(client_id=client_id, client_secret=client_secret, scopes=scopes, certificate=cert, key=key)
        >>> boleto = Boleto(configs)
        >>> num_boleto = '00123456789'
        >>> detail = boleto.consulta_detalhada(num_boleto)
        >>> pprint(detail)

        """
        detail = get_boleto_detail(nosso_numero, self.configs, self.auth_token)
        self._numero = nosso_numero
        return detail

    @overload
    def consulta_pdf(self, nosso_numero: str) -> BytesIO:
        ...

    @overload
    def consulta_pdf(self, nosso_numero: str, filename: PathType) -> None:
        ...

    def consulta_pdf(
        self, nosso_numero: str, filename: Optional[PathType] = None
    ) -> Optional[BytesIO]:
        """Captura o boleto em um buffer na memória ou em arquivo.

        Escopo requerido: ScopeEnum.BOLETO_COBRANCA_READ

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
        >>> from pyinterboleto import Boleto, RequestConfigs, ScopeEnum
        >>> direc = Path('caminho/para/pasta/com/certificados')
        >>> cert = direc / 'Inter API_Certificado.crt'
        >>> key = direc / 'Inter API_Chave.key'
        >>> # client_id e client_secret são obtidos de acordo com a documentação do Inter
        >>> client_id = 'valor-do-id-uuid'
        >>> client_secret = 'valor-do-secret-uuid'
        >>> scopes = (ScopeEnum.BOLETO_COBRANCA_READ,)
        >>> configs = RequestConfigs(client_id=client_id, client_secret=client_secret, scopes=scopes, certificate=cert, key=key)
        >>> boleto = Boleto(configs)
        >>> configs = RequestConfigs(conta_inter=acc, certificate=cert, key=key)
        >>> boleto = Boleto(configs)
        >>> num_boleto = '00123456789'
        >>> pdf = boleto.consulta_pdf(num_boleto)

        """
        pdf: Union[None, BytesIO]
        if filename is None:
            pdf = get_pdf_boleto_in_memory(nosso_numero, self.configs, self.auth_token)
        else:
            pdf = get_pdf_boleto_to_file(
                nosso_numero, filename, self.configs, self.auth_token
            )

        self._numero = nosso_numero
        return pdf

    def consulta_lista(
        self,
        data_inicial: date,
        data_final: date,
        filtrar_data_por: FiltrarDataPorEnum = FiltrarDataPorEnum.VENCIMENTO,
        situacao: Optional[Iterable[SituacaoEnum]] = None,
        nome: Optional[str] = None,
        email: Optional[str] = None,
        cpf_cnpj: Optional[str] = None,
        itens_por_pagina: int = 100,
        pagina_atual: int = 0,
        ordenar: OrdenarEnum = OrdenarEnum.PAGADOR,
        tipo_ordenacao: Literal["ASC", "DESC"] = "ASC",
    ) -> ResponseList:
        """Recupera uma coleção de boletos por um período específico, de acordo
        com os parametros informados.

        Está pesquisa retorna os boletos no padrão D+1, ou seja, os boletos
        inseridos na data atual só serão visíveis a partir do dia seguinte.

        Escopo requerido: ScopeEnum.BOLETO_COBRANCA_READ

        Parameters
        ----------
        data_inicial : date
            Data de início para o filtro. Esta data corresponde a data de
            vencimento dos títulos. Isto é, a filtragem vai incluir títulos com
            data de vencimento A PARTIR desta data.

        data_final : date
            Data de fim para o filtro. Esta data corresponde a data de vencimento
            dos títulos. Isto é, a filtragem vai incluir títulos com data de
            vencimento até esta data.

        filtrar_data_por : FiltrarDataPorEnum, optional
            Veja documentação do enum FiltrarDataPorEnum, VENCIMENTO caso não seja
            especificado.

        situacao : Optional[Iterable[SituacaoEnum]], optional
            Filtro pela situação da cobrança. Aceita multiplos valores, None caso não
            seja especificado.

        nome : Optional[str], optional
            Filtro pelo nome do pagador, None caso não seja especificado.

        email : Optional[str], optional
            Filtro pelo email do pagador, None caso não seja especificado.

        cpf_cnpj : Optional[str], optional
            Filtro pelo CPF ou CNPJ do pagador, None caso não seja especificado.

        ordenar : OrdenarEnum, optional
            Opção de ordenação do retorno da consulta, PAGADOR caso não seja
            especificado.

        itens_por_pagina : int, optional
            Quantidade máxima de registros retornados em cada página. Apenas a última
            página pode conter uma quantidade menor de registros, 100 itens caso não
            seja especificado.

            Valor mínimo: 1
            Valor máximo: 1000

        pagina_atual : int, optional
            Página a ser retornada pela consulta. Se não informada, assumirá que será 0.

        tipo_ordenacao : 'ASC' | 'DESC', optional
            Opção para tipo de ordenação, 'ASC' caso não seja especificado.


        Returns
        -------
        ResponseList
            Resultado da busca.

        Examples
        --------
        >>> from pathlib import Path
        >>> from pprint import pprint
        >>> from datetime import date, timedelta
        >>> from pyinterboleto import Boleto, RequestConfigs, ScopeEnum
        >>> direc = Path('caminho/para/pasta/com/certificados')
        >>> cert = direc / 'Inter API_Certificado.crt'
        >>> key = direc / 'Inter API_Chave.key'
        >>> # client_id e client_secret são obtidos de acordo com a documentação do Inter
        >>> client_id = 'valor-do-id-uuid'
        >>> client_secret = 'valor-do-secret-uuid'
        >>> scopes = (ScopeEnum.BOLETO_COBRANCA_READ,)
        >>> configs = RequestConfigs(client_id=client_id, client_secret=client_secret, scopes=scopes, certificate=cert, key=key)
        >>> boleto = Boleto(configs)
        >>> inicial = date.today() - timedelta(days=30)
        >>> final = date.today()
        >>> lista = boleto.consulta_lista(inicial, final)
        >>> pprint(lista)
        """
        lista = get_lista_boletos(
            token=self.auth_token,
            configs=self.configs,
            data_inicial=data_inicial,
            data_final=data_final,
            filtrar_data_por=filtrar_data_por,
            situacao=situacao,
            nome=nome,
            email=email,
            cpf_cnpj=cpf_cnpj,
            itens_por_pagina=itens_por_pagina,
            pagina_atual=pagina_atual,
            ordenar=ordenar,
            tipo_ordenacao=tipo_ordenacao,
        )
        return lista

    def baixar_boleto(self, nosso_numero: str, codigo_baixa: CodigoBaixaEnum) -> None:
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
        >>> from pyinterboleto import Boleto, RequestConfigs, CodigoBaixaEnum, ScopeEnum
        >>> direc = Path('caminho/para/pasta/com/certificados')
        >>> cert = direc / 'Inter API_Certificado.crt'
        >>> key = direc / 'Inter API_Chave.key'
        >>> # client_id e client_secret são obtidos de acordo com a documentação do Inter
        >>> client_id = 'valor-do-id-uuid'
        >>> client_secret = 'valor-do-secret-uuid'
        >>> scopes = (ScopeEnum.EXTRATO_READ, ScopeEnum.BOLETO_COBRANCA_READ)
        >>> configs = RequestConfigs(client_id=client_id, client_secret=client_secret, scopes=scopes, certificate=cert, key=key)
        >>> boleto = Boleto(configs)
        >>> num_boleto = '00123456789'
        >>> boleto.baixar_boleto(num_boleto, CodigoBaixaEnum.PC)

        """
        executa_baixa(nosso_numero, codigo_baixa, self.configs)
