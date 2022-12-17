from unittest.mock import Mock, patch

from src.pyinterboleto.boleto import Boleto
from src.pyinterboleto.common.tipo_pessoa import TipoPessoa
from src.pyinterboleto.emissao.beneficiario import Beneficiario
from src.pyinterboleto.emissao.emissor import Emissao
from src.pyinterboleto.emissao.pagador import Pagador
from src.pyinterboleto.utils.requests import RequestConfigs


def test_create(request_configs: RequestConfigs, patched_auth_request: Mock):
    boleto = Boleto(request_configs)
    with patch("src.pyinterboleto.emissao.emissor.post") as patched_post:
        mocked_reponse = Mock()
        mocked_reponse.status_code = 200
        mocked_reponse.json = Mock(
            return_value={
                "seuNumero": "00001",
                "nossoNumero": "00123456789",
                "codigoBarras": "00000000000000000000000000000000000000000000",
                "linhaDigitavel": "00000000000000000000000000000000000000000000000",
            }
        )
        patched_post.return_value = mocked_reponse

        pagador = Pagador(
            cpfCnpj="12.345.678/0001-12",
            tipoPessoa=TipoPessoa.JURIDICA,
            nome="Alguma Empresa LTDA",
            endereco="Qulaquer um",
            cidade="Também do Brasil",
            uf="SP",
            cep="12345-678",
        )
        beneficiario = Beneficiario(
            cpfCnpj="123.456.789-01",
            tipoPessoa=TipoPessoa.FISICA,
            nome="Algum Nome de Pessoa",
            endereco="Algum lugar",
            bairro="Qualquer",
            cidade="Do Brasil",
            uf="SP",
            cep="12345-678",
        )
        dados = Emissao(
            pagador=pagador,
            beneficiario=beneficiario,
            seuNumero="00001",
            valorNominal=10.01,
            dataVencimento="2023-01-01",
            numDiasAgenda=25,
        )
        boleto.emitir(dados)

    patched_auth_request.assert_called_once()
    patched_post.assert_called_once()
