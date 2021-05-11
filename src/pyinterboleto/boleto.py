from datetime import date
from io import BytesIO
from typing import Optional, Union, overload

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

    @property
    def configs(self) -> RequestConfigs:
        return self._configs

    @property
    def emitido(self) -> bool:
        return self._emitido

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
        """
        if self.emitido or self.numero != '':
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
            Data de início para o filtro.

        data_final : date
            Data de fim para o filtro.

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
        """
        lista = get_lista_boletos(data_inicial, data_final, self.configs,
                                  filtrar=filtrar, ordernar=ordernar,
                                  page=page, size=size)
        return lista
