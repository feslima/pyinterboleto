# PyInterBoleto
Biblioteca para facilitar o manuseio de boletos de contas PJ no Banco Inter.

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
>>> from pprint import pprint
>>> from pyinterboleto import RequestConfigs
>>> 
>>> # definição da configuração de autenticação
>>> direc = Path('caminho/para/pasta/com/certificados')
>>> cert = direc / 'Inter API_Certificado.crt'
>>> key = direc / 'Inter API_Chave.key'
>>> acc = '12345678' # Número da conta PJ
>>> configs = RequestConfigs(conta_inter=acc, certificate=cert, key=key)
```

## Emissão de boleto
_*Os dados a seguir são fictícios. Não os utilize do jeito que estão!*_

```python
>>> from pyinterboleto import Boleto, Emissao, Pagador, RequestConfigs
>>> boleto = Boleto(configs) # configs vem da seção configuração
>>>
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
>>>
>>> emissao = Emissao(
...     pagador=pagador, seuNumero='00001',
...     cnpjCPFBeneficiario='12.345.678/0001-01',
...     valorNominal=0.01,
...     dataEmissao=date.today(),
...     dataVencimento=date.today()+timedelta(days=2)
... )
>>>
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
>>> print(detail)
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
>>> print(lista)
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

Como a API do Inter não possui ambiente de sandboxing, optei por não implementar rotinas de testes. Isto é, o Inter fornece uma cota sem custo adicional de 100 boletos emitidos por mês. Acima disto, é preciso pagar mais.

Como é um recurso bem limitado, não faz sentido implementar uma suíte de testes para emissão e baixa de boletos. No caso de consultas, é possível sim. So não implementei por pura falta de tempo (~~e preguiça também~~).