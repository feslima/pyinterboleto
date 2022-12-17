# PyInterBoleto
Biblioteca para facilitar o manuseio de boletos de contas PJ no Banco Inter.

[![PyPI version](https://badge.fury.io/py/pyinterboleto.svg)](https://badge.fury.io/py/pyinterboleto) [![codecov](https://codecov.io/gh/feslima/pyinterboleto/branch/main/graph/badge.svg?token=T2SJ0P8KPG)](https://codecov.io/gh/feslima/pyinterboleto)

***
- [PyInterBoleto](#pyinterboleto)
- [Instalação](#instalação)
- [Documentação](#documentação)
- [Usagem básica](#usagem-básica)
  - [Configuração de autenticação](#configuração-de-autenticação)
  - [Emissão de boleto](#emissão-de-boleto)
  - [Consultas](#consultas)
    - [Consulta detalhada de boletos individuais](#consulta-detalhada-de-boletos-individuais)
    - [Consulta de coleção de boletos](#consulta-de-coleção-de-boletos)
    - [Resgate de PDFs de boletos individuais](#resgate-de-pdfs-de-boletos-individuais)
  - [Baixa de boleto](#baixa-de-boleto)
- [Testagem](#testagem)

# Instalação
Basta executar o comando via pip:
```
pip install pyinterboleto
```

# Documentação
A maioria das classes, métodos, funções e estruturas de dados já contém uma documentação habilitada para uso em IDEs no estilo [numpy docstring](https://numpydoc.readthedocs.io/en/latest/format.html).

Foi optado por não fazer uma documentação exclusiva (no estilo readthedocs) devido a ser uma biblioteca relativamente pequena.

Sendo assim, o pacote está organizado em três submódulos principais: **emissão** (os dados necessários na emissão são organizados em estruturas menores. São elas dados de: [emissão](src/pyinterboleto/emissao/emissor.py), [pagador](src/pyinterboleto/emissao/pagador.py), [desconto](src/pyinterboleto/emissao/desconto.py), [multa](src/pyinterboleto/emissao/multa.py), [mora](src/pyinterboleto/emissao/mora.py) e [mensagem](src/pyinterboleto/emissao/mensagem.py)), **consulta** ([detalhada](src/pyinterboleto/consulta/detalhado.py), [coleção](src/pyinterboleto/consulta/lista.py) e [PDF](src/pyinterboleto/consulta/pdf.py)) e [**baixa**](src/pyinterboleto/baixa/__init__.py) de boletos.

Em cada um desses links se encontram as funções e objetos com suas respectivas documentações, caso seja preciso mais informações.
# Usagem básica
A classe principal que tem todas as funcionalidades requeridas para a API se chama [**`Boleto`**](src/pyinterboleto/boleto.py). Através dela que todas as operações de emissão, consulta e baixa feitas.

No entanto, como consta na documentação do Banco Inter, para se ter acesso a API é preciso emitir a chave e o certificado de acesso desta. Antes de utilizar este pacote, certifique-se que você já possui estes arquivos.

Feito isto, alguns exemplos de manuseio são mostrados nas seções à seguir.
***

## Configuração de autenticação
Antes de fazer qualquer requisição à API do Inter é preciso antes definir o [objeto de configuração](src/pyinterboleto/utils/requests.py) para autenticação e autorização:

```python
>>> from pathlib import Path
>>> from datetime import date, timedelta
>>> from prettyprinter import pprint, install_extras
>>> from pyinterboleto import RequestConfigs
>>>
>>> install_extras()
>>>
>>> # definição da configuração de autenticação
>>> direc = Path('caminho/para/pasta/com/certificados')
>>> cert = direc / 'Inter API_Certificado.crt'
>>> key = direc / 'Inter API_Chave.key'
>>> # client_id e client_secret são obtidos de acordo com a documentação do Inter
>>> client_id = 'valor-do-id-uuid'
>>> client_secret = 'valor-do-secret-uuid'
>>> scopes = (ScopeEnum.BOLETO_COBRANCA_WRITE,)
>>> configs = RequestConfigs(client_id=client_id, client_secret=client_secret, scopes=scopes, certificate=cert, key=key)
```

## Emissão de boleto
_*Os dados a seguir são fictícios. Não os utilize do jeito que estão!*_

```python
>>> from pyinterboleto import Boleto, Emissao, Pagador, Beneficiario
>>> boleto = Boleto(configs) # configs vem da seção configuração
>>>
>>> pagador = Pagador(
...     cpfCnpj="12.345.678/0001-12",
...     tipoPessoa=TipoPessoa.JURIDICA,
...     nome="Alguma Empresa LTDA",
...     endereco="Qulaquer um",
...     cidade="Também do Brasil",
...     uf="SP",
...     cep="12345-678",
... )
>>> beneficiario = Beneficiario(
...     cpfCnpj="123.456.789-01",
...     tipoPessoa=TipoPessoa.FISICA,
...     nome="Algum Nome de Pessoa",
...     endereco="Algum lugar",
...     bairro="Qualquer",
...     cidade="Do Brasil",
...     uf="SP",
...     cep="12345-678",
... )
>>> dados = Emissao(
...     pagador=pagador,
...     beneficiario=beneficiario,
...     seuNumero="000001",
...     valorNominal=10.01,
...     dataVencimento="2023-01-01",
...     numDiasAgenda=25,
... )
>>> result = boleto.emitir(emissao)
>>> print(result)
{'seuNumero': '00001', 'nossoNumero': '00123456789',
 'codigoBarras': '00000000000000000000000000000000000000000000',
 'linhaDigitavel': '00000000000000000000000000000000000000000000000'}
>>>
```

## Consultas
Há três categorias de consultas disponíveis: detalhamento individual de boletos, coleção de boletos e resgate de arquivos .pdf.

### Consulta detalhada de boletos individuais
É preciso saber o número de identificação do título antes de fazer esta requisição. Este número pode ser obtido quando a emissão do título é bem sucedida (chave `nossoNumero` do dicionário de resposta na seção anterior)
ou quando se faz a filtragem de coleções de boletos.

```python
>>> boleto = Boleto(configs)
>>> num_boleto = '00123456789' # numero de identificação do título pelo Inter
>>> detail = boleto.consulta_detalhada(num_boleto)
>>> pprint(detail)
pyinterboleto.consulta.detalhado.BoletoDetail(
    nomeBeneficiario='NOME DO BENEFICIARIO CONTA PJ',
    cnpjCpfBeneficiario='00000000000000',
    tipoPessoaBeneficiario='JURIDICA',
    dataHoraSituacao=datetime.datetime(2021, 5, 10),
    codigoBarras='00000000000000000000000000000000000000000000',
    linhaDigitavel='00000000000000000000000000000000000000000000000',
    dataVencimento=datetime.date(2021, 5, 11),
    dataEmissao=datetime.date(2021, 5, 9),
    seuNumero='00001',
    valorNominal=0.01,
    nomePagador='Pessoa Ficticia da Silva',
    emailPagador='',
    dddPagador='',
    telefonePagador='',
    tipoPessoaPagador='FISICA',
    cnpjCpfPagador='12345678909',
    codigoEspecie='OUTROS',
    dataLimitePagamento=datetime.date(2021, 6, 10),
    valorAbatimento=0.0,
    situacao='PAGO',
    desconto1=pyinterboleto.common.desconto.DescontoConsulta(
        codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
    ),
    desconto2=pyinterboleto.common.desconto.DescontoConsulta(
        codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
    ),
    desconto3=pyinterboleto.common.desconto.DescontoConsulta(
        codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
    ),
    multa=pyinterboleto.common.multa.MultaConsulta(
        codigo=pyinterboleto.common.multa.CodigoMultaEnum.NTM
    ),
    mora=pyinterboleto.common.mora.MoraConsulta(
        codigo=pyinterboleto.common.mora.CodigoMoraEnum.I
    ),
    situacaoPagamento='BAIXADO',
    valorTotalRecebimento=0.01
)
>>>
```

### Consulta de coleção de boletos
As datas de início e final da filtragem são obrigatórias, [há outras definições de elementos de filtragem opcionais](src/pyinterboleto/consulta/lista.py).

```python
>>> from datetime import date, timedelta
>>> boleto = Boleto(configs)
>>> inicial = date.today() - timedelta(days=30)
>>> final = date.today()
>>> lista = boleto.consulta_lista(inicial, final)
>>> pprint(lista)
pyinterboleto.consulta.lista.ResponseList(
    totalPages=1,
    totalElements=8,
    numberOfElements=8,
    last=True,
    first=True,
    size=20,
    summary=pyinterboleto.consulta.lista.Summary(
        recebidos=pyinterboleto.consulta.lista.SummaryContent(
            quantidade=1,
            valor=0.01
        ),
        previstos=pyinterboleto.consulta.lista.SummaryContent(
            quantidade=2,
            valor=66.2
        ),
        baixados=pyinterboleto.consulta.lista.SummaryContent(
            quantidade=2,
            valor=0.02
        ),
        expirados=pyinterboleto.consulta.lista.SummaryContent(
            quantidade=3,
            valor=38.01
        )
    ),
    content=[
        pyinterboleto.consulta.lista.BoletoItem(
            nossoNumero='00000000000',
            seuNumero='00001',
            cnpjCpfSacado='1234567809',
            nomeSacado='Pessoa Ficticia da Silva',
            situacao='PAGO',
            dataVencimento=datetime.date(2021, 5, 11),
            valorNominal=0.01,
            email='',
            telefone='',
            dataEmissao=datetime.date(2021, 5, 9),
            dataLimite=datetime.date(2021, 6, 10),
            linhaDigitavel='00000000000000000000000000000000000000000000000',
            desconto1=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            desconto2=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            desconto3=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            multa=pyinterboleto.common.multa.MultaConsulta(
                codigo=pyinterboleto.common.multa.CodigoMultaEnum.NTM
            ),
            mora=pyinterboleto.common.mora.MoraConsulta(
                codigo=pyinterboleto.common.mora.CodigoMoraEnum.I
            ),
            valorAbatimento=0.0,
            dataPagtoBaixa=datetime.date(2021, 5, 10),
            valorTotalRecebimento=0.01
        ),
        pyinterboleto.consulta.lista.BoletoItem(
            nossoNumero='00000000000',
            seuNumero='00002',
            cnpjCpfSacado='1234567809',
            nomeSacado='Pessoa Ficticia da Silva',
            situacao='EXPIRADO',
            dataVencimento=datetime.date(2021, 5, 12),
            valorNominal=0.01,
            email='',
            telefone='',
            dataEmissao=datetime.date(2021, 5, 10),
            dataLimite=datetime.date(2021, 6, 11),
            linhaDigitavel='00000000000000000000000000000000000000000000000',
            desconto1=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            desconto2=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            desconto3=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            multa=pyinterboleto.common.multa.MultaConsulta(
                codigo=pyinterboleto.common.multa.CodigoMultaEnum.NTM
            ),
            mora=pyinterboleto.common.mora.MoraConsulta(
                codigo=pyinterboleto.common.mora.CodigoMoraEnum.I
            ),
            valorAbatimento=0.0
        ),
        pyinterboleto.consulta.lista.BoletoItem(
            nossoNumero='00000000000',
            seuNumero='00003',
            cnpjCpfSacado='1234567809',
            nomeSacado='Pessoa Ficticia da Silva',
            situacao='BAIXADO',
            dataVencimento=datetime.date(2021, 5, 13),
            valorNominal=0.01,
            email='',
            telefone='',
            dataEmissao=datetime.date(2021, 5, 11),
            dataLimite=datetime.date(2021, 6, 12),
            linhaDigitavel='00000000000000000000000000000000000000000000000',
            desconto1=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            desconto2=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            desconto3=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            multa=pyinterboleto.common.multa.MultaConsulta(
                codigo=pyinterboleto.common.multa.CodigoMultaEnum.NTM
            ),
            mora=pyinterboleto.common.mora.MoraConsulta(
                codigo=pyinterboleto.common.mora.CodigoMoraEnum.I
            ),
            valorAbatimento=0.0,
            dataPagtoBaixa=datetime.date(2021, 5, 11)
        ),
        pyinterboleto.consulta.lista.BoletoItem(
            nossoNumero='00000000000',
            seuNumero='00003',
            cnpjCpfSacado='1234567809',
            nomeSacado='Pessoa Ficticia da Silva',
            situacao='BAIXADO',
            dataVencimento=datetime.date(2021, 5, 13),
            valorNominal=0.01,
            email='',
            telefone='',
            dataEmissao=datetime.date(2021, 5, 11),
            dataLimite=datetime.date(2021, 6, 12),
            linhaDigitavel='00000000000000000000000000000000000000000000000',
            desconto1=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            desconto2=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            desconto3=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            multa=pyinterboleto.common.multa.MultaConsulta(
                codigo=pyinterboleto.common.multa.CodigoMultaEnum.NTM
            ),
            mora=pyinterboleto.common.mora.MoraConsulta(
                codigo=pyinterboleto.common.mora.CodigoMoraEnum.I
            ),
            valorAbatimento=0.0,
            dataPagtoBaixa=datetime.date(2021, 5, 11)
        ),
        pyinterboleto.consulta.lista.BoletoItem(
            nossoNumero='00000000000',
            seuNumero='00004',
            cnpjCpfSacado='1234567809',
            nomeSacado='Pessoa Ficticia da Silva',
            situacao='EXPIRADO',
            dataVencimento=datetime.date(2021, 6, 1),
            valorNominal=20.0,
            email='',
            telefone='',
            dataEmissao=datetime.date(2021, 5, 30),
            dataLimite=datetime.date(2021, 7, 1),
            linhaDigitavel='00000000000000000000000000000000000000000000000',
            desconto1=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            desconto2=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            desconto3=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            multa=pyinterboleto.common.multa.MultaConsulta(
                codigo=pyinterboleto.common.multa.CodigoMultaEnum.NTM
            ),
            mora=pyinterboleto.common.mora.MoraConsulta(
                codigo=pyinterboleto.common.mora.CodigoMoraEnum.I
            ),
            valorAbatimento=0.0
        ),
        pyinterboleto.consulta.lista.BoletoItem(
            nossoNumero='00000000000',
            seuNumero='00005',
            cnpjCpfSacado='1234567809',
            nomeSacado='Pessoa Ficticia da Silva',
            situacao='EXPIRADO',
            dataVencimento=datetime.date(2021, 7, 9),
            valorNominal=18.0,
            email='',
            telefone='',
            dataEmissao=datetime.date(2021, 7, 7),
            dataLimite=datetime.date(2021, 8, 8),
            linhaDigitavel='00000000000000000000000000000000000000000000000',
            desconto1=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            desconto2=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            desconto3=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            multa=pyinterboleto.common.multa.MultaConsulta(
                codigo=pyinterboleto.common.multa.CodigoMultaEnum.NTM
            ),
            mora=pyinterboleto.common.mora.MoraConsulta(
                codigo=pyinterboleto.common.mora.CodigoMoraEnum.I
            ),
            valorAbatimento=0.0
        ),
        pyinterboleto.consulta.lista.BoletoItem(
            nossoNumero='00000000000',
            seuNumero='00006',
            cnpjCpfSacado='1234567809',
            nomeSacado='Pessoa Ficticia da Silva',
            situacao='VENCIDO',
            dataVencimento=datetime.date(2021, 8, 10),
            valorNominal=43.0,
            email='',
            telefone='',
            dataEmissao=datetime.date(2021, 8, 7),
            dataLimite=datetime.date(2021, 9, 9),
            linhaDigitavel='00000000000000000000000000000000000000000000000',
            desconto1=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            desconto2=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            desconto3=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            multa=pyinterboleto.common.multa.MultaConsulta(
                codigo=pyinterboleto.common.multa.CodigoMultaEnum.NTM
            ),
            mora=pyinterboleto.common.mora.MoraConsulta(
                codigo=pyinterboleto.common.mora.CodigoMoraEnum.I
            ),
            valorAbatimento=0.0
        ),
        pyinterboleto.consulta.lista.BoletoItem(
            nossoNumero='00000000000',
            seuNumero='00007',
            cnpjCpfSacado='1234567809',
            nomeSacado='Pessoa Ficticia da Silva',
            situacao='VENCIDO',
            dataVencimento=datetime.date(2021, 8, 10),
            valorNominal=23.2,
            email='',
            telefone='',
            dataEmissao=datetime.date(2021, 8, 7),
            dataLimite=datetime.date(2021, 9, 9),
            linhaDigitavel='00000000000000000000000000000000000000000000000',
            desconto1=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            desconto2=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            desconto3=pyinterboleto.common.desconto.DescontoConsulta(
                codigo=pyinterboleto.common.desconto.CodigoDescontoEnum.NTD
            ),
            multa=pyinterboleto.common.multa.MultaConsulta(
                codigo=pyinterboleto.common.multa.CodigoMultaEnum.NTM
            ),
            mora=pyinterboleto.common.mora.MoraConsulta(
                codigo=pyinterboleto.common.mora.CodigoMoraEnum.I
            ),
            valorAbatimento=0.0
        )
    ]
)
>>>
```

### Resgate de PDFs de boletos individuais
Assim como na consulta detalhada individual, é preciso saber o número de identificação do título antes de fazer a requisição. Há dois modos de como o PDF é armazendo: em memória ou salvo diretamento em um arquivo especificado.

```python
>>> from pathlib import Path
>>> boleto = Boleto(configs)
>>> num_boleto = '00123456789'
>>> # Armazenado em um buffer de bytes na memória
>>> pdf = boleto.consulta_pdf(num_boleto)
>>>
>>> # salva em um arquivo chamado 'boleto.pdf' no diretório atual
>>> filename = Path().resolve() / 'boleto.pdf'
>>> boleto.consulta_pdf(num_boleto, filename)
>>>
```

***

## Baixa de boleto
Também é preciso saber o número de identificação do título. Os tipos de baixas são definidos no enum [`CodigoBaixaEnum`](src/pyinterboleto/baixa/__init__.py).

```python
>>> from pyinterboleto import CodigoBaixaEnum
>>> boleto = Boleto(configs)
>>> num_boleto = '00123456789'
>>> boleto.baixar_boleto(num_boleto, CodigoBaixaEnum.PC)
>>>
```

***

# Testagem

Como a API do Inter não possui ambiente de sandboxing, optei por não implementar rotinas de testes para todas operações, apenas as de consulta. Isto é, o Inter fornece uma cota sem custo adicional de 100 boletos emitidos por mês. Acima disto, é preciso pagar mais.

Como é um recurso bem limitado, não faz sentido implementar uma suíte de testes para emissão e baixa de boletos.

Para realizar os testes localmente, clone o repositório e crie um arquivo chamado `inter.env` na raiz do projeto que tem o seguinte formato:

```
INTER_ACC=''
INTER_API_KEY='-----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----
'
INTER_API_CERTIFICATE='-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----'
```

As variáveis `INTER_ACC`, `INTER_API_KEY` e `INTER_API_CERTIFICATE` são o número da conta Inter (apenas números), contéudos do arquivo `.key` e `.crt` respectivamente.

Instale as dependências de desenvolvimento:
```shell
# pode usar o gerenciador que quiser (e.g. poetry, conda, etc.)
pip install -r requirements-dev.txt
```

Para rodar os tests:
```shell
pytest
```
