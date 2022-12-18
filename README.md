# PyInterBoleto

Biblioteca para facilitar o manuseio de boletos de contas PJ no Banco Inter.

[![PyPI version](https://badge.fury.io/py/pyinterboleto.svg)](https://badge.fury.io/py/pyinterboleto)
[![codecov](https://codecov.io/gh/feslima/pyinterboleto/branch/main/graph/badge.svg?token=T2SJ0P8KPG)](https://codecov.io/gh/feslima/pyinterboleto)

***

- [PyInterBoleto](#pyinterboleto)
- [Instalação](#instalação)
- [Documentação](#documentação)
- [Utilização básica](#utilização-básica)
  - [Configuração de autenticação](#configuração-de-autenticação)
  - [Emissão de boleto](#emissão-de-boleto)
  - [Consultas](#consultas)
    - [Consulta detalhada de boletos individuais](#consulta-detalhada-de-boletos-individuais)
    - [Consulta de coleção de boletos](#consulta-de-coleção-de-boletos)
    - [Resgate de PDFs de boletos individuais](#resgate-de-pdfs-de-boletos-individuais)
  - [Baixa de boleto](#baixa-de-boleto)
- [Testagem](#testagem)

## Instalação

Basta executar o comando via pip (ou poetry):

```shell
pip install pyinterboleto
# ou via poetry
poetry add pyinterboleto
```

## Documentação

A maioria das classes, métodos, funções e estruturas de dados já contém uma
documentação habilitada para uso em IDEs no estilo
[numpy docstring](https://numpydoc.readthedocs.io/en/latest/format.html).

Foi optado por não fazer uma documentação exclusiva (no estilo readthedocs)
devido a ser uma biblioteca relativamente pequena.

Sendo assim, o pacote está organizado em três submódulos principais:
**emissão** (os dados necessários na emissão são organizados em estruturas
menores. São elas dados de: [emissão](src/pyinterboleto/emissao/emissor.py),
[pagador](src/pyinterboleto/emissao/pagador.py),
[desconto](src/pyinterboleto/emissao/desconto.py),
[multa](src/pyinterboleto/emissao/multa.py),
[mora](src/pyinterboleto/emissao/mora.py) e
[mensagem](src/pyinterboleto/emissao/mensagem.py)), **consulta**
([detalhada](src/pyinterboleto/consulta/detalhado.py),
[coleção](src/pyinterboleto/consulta/lista.py) e
[PDF](src/pyinterboleto/consulta/pdf.py)) e
[**cancelamento**](src/pyinterboleto/baixa.py) de boletos.

Em cada um desses links se encontram as funções e objetos com suas
respectivas documentações, caso seja preciso mais informações.

## Utilização básica

A classe principal que tem todas as funcionalidades requeridas para a API se
chama [**`Boleto`**](src/pyinterboleto/boleto.py). Através dela que todas as
operações de emissão, consulta e baixa feitas.

No entanto, como consta na documentação do Banco Inter, para se ter acesso a
API é preciso emitir a chave e o certificado de acesso desta. Antes de
utilizar este pacote, certifique-se que você já possui estes arquivos.

Feito isto, alguns exemplos de manuseio são mostrados nas seções à seguir.
***

### Configuração de autenticação

Antes de fazer qualquer requisição à API do Inter é preciso antes definir o
[objeto de configuração](src/pyinterboleto/utils/requests.py) para
autenticação e autorização:

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

### Emissão de boleto

**Os dados a seguir são fictícios. Não os utilize do jeito que estão!**

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

### Consultas

Há três categorias de consultas disponíveis: detalhamento individual de
boletos, coleção de boletos e resgate de arquivos .pdf.

#### Consulta detalhada de boletos individuais

É preciso saber o número de identificação do título antes de fazer esta
requisição. Este número pode ser obtido quando a emissão do título é
bem sucedida (chave `nossoNumero` do dicionário de resposta na seção anterior)
ou quando se faz a filtragem de coleções de boletos.

```python
>>> boleto = Boleto(configs)
>>> num_boleto = '00123456789' # numero de identificação do título pelo Inter
>>> detail = boleto.consulta_detalhada(num_boleto)
>>> pprint(detail)
```

#### Consulta de coleção de boletos

As datas de início e final da filtragem são obrigatórias,
[há outras definições de elementos de filtragem opcionais](src/pyinterboleto/consulta/lista.py).

```python
>>> from datetime import date, timedelta
>>> boleto = Boleto(configs)
>>> inicial = date.today() - timedelta(days=30)
>>> final = date.today()
>>> lista = boleto.consulta_lista(inicial, final)
>>> pprint(lista)
```

#### Resgate de PDFs de boletos individuais

Assim como na consulta detalhada individual, é preciso saber o número de
identificação do título antes de fazer a requisição. Há dois modos de
como o PDF é armazendo: em memória ou salvo diretamento em um arquivo especificado.

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
```

***

### Cancelamento de boleto

Também é preciso saber o número de identificação do título. Os tipos de
baixas são definidos no enum [`MotivoCancelamentoEnum`](src/pyinterboleto/baixa.py).

```python
>>> from pyinterboleto import MotivoCancelamentoEnum
>>> boleto = Boleto(configs)
>>> num_boleto = '00123456789'
>>> boleto.cancelar_boleto(num_boleto, MotivoCancelamentoEnum.A_PEDIDO_DO_CLIENTE)
```

***

### Testes

Como a API do Inter não possui ambiente de sandboxing, optei por
"mockar" todas as repostas de acordo com a documentação oficial
deles. Isso não isenta a biblioteca de bugs, tendo em vista que a
própria documentação deles apresenta algumas inconsistências.

Para realizar os testes localmente, clone o repositório e instale as
dependências de desenvolvimento:

```shell
# pode usar o gerenciador que quiser (e.g. poetry, conda, etc.)
pip install -r requirements-dev.txt

# poetry install --no-root (para o caso de usar poetry).
```

Para rodar os tests:

```shell
pytest

# ou no caso de poetry:
poetry run poe cov_local
```
