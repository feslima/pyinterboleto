from base64 import b64encode
from unittest.mock import Mock, patch

from src.pyinterboleto import Boleto, RequestConfigs


def get_mocked_detail_response():
    return {
        "nomeBeneficiario": "nome do beneficiario",
        "cnpjCpfBeneficiario": "CNPJ/CPF do beneficiario",
        "tipoPessoaBeneficiario": "tipo do beneficiario",
        "contaCorrente": "conta corrente",
        "nossoNumero": "numero Inter do boleto",
        "seuNumero": "numero Cliente do boleto",
        "pagador": {
            "cpfCnpj": "CPF/CNPJ do pagador",
            "tipoPessoa": "tipo do pagador",
            "nome": "nome completo do pagador",
            "endereco": "logradouro do pagador",
            "cidade": "cidade do pagador",
            "uf": "uf",
            "cep": "cedp",
            "numero": "numero no logradouro",
            "complemento": "complemento do logradouro",
            "bairro": "bairro",
            "email": "email do pagador",
            "ddd": "ddd",
            "telefone": "telefone do pagador",
        },
        "motivoCancelamento": "motivo, caso haja",
        "situacao": "situacao do boleto",
        "dataHoraSituacao": "2022-03-08 00:00",
        "dataVencimento": "2022-01-31",
        "valorNominal": 10.00,
        "dataEmissao": "2022-01-27",
        "dataLimite": "2022-01-31",
        "codigoEspecie": "OUTROS",
        "codigoBarras": "codigo de barras do boleto",
        "linhaDigitavel": "linha digitavel do boleto",
        "origem": "origem da inclusào do boleto",
        "mensagem": {"linha1": "linha 1 da mensagem"},
        "desconto1": {"codigo": "NAOTEMDESCONTO", "taxa": 0.00, "valor": 0.00},
        "desconto2": {"codigo": "NAOTEMDESCONTO", "taxa": 0.00, "valor": 0.00},
        "desconto3": {"codigo": "NAOTEMDESCONTO", "taxa": 0.00, "valor": 0.00},
        "multa": {"codigo": "NAOTEMMULTA", "taxa": 0.00, "valor": 0.00},
        "mora": {"codigo": "ISENTO", "taxa": 0.00, "valor": 0.00},
        "valorAbatimento": 10.00,
    }


def test_detailed(request_configs: RequestConfigs, patched_auth_request: Mock):
    """ "Acts as smoke test. No real functionality to be tested besides the
    dataclass creation and processing."""
    boleto = Boleto(request_configs)

    with patch("src.pyinterboleto.consulta.detalhado.get") as patched_get:
        mocked_reponse = Mock()
        mocked_reponse.status_code = 200
        mocked_reponse.json = Mock(return_value=get_mocked_detail_response())
        patched_get.return_value = mocked_reponse

        detail = boleto.consulta_detalhada("01234567891")
        assert detail.pagador.cpfCnpj == "CPF/CNPJ do pagador"

    patched_auth_request.assert_called_once()
    patched_get.assert_called_once()


def test_pdf(request_configs: RequestConfigs, patched_auth_request: Mock):
    boleto = Boleto(request_configs)

    with patch("src.pyinterboleto.consulta.pdf.get") as patched_get:
        mocked_reponse = Mock()
        mocked_reponse.status_code = 200
        mocked_reponse.content = b64encode("some dummy pdf.data".encode("utf-8"))
        patched_get.return_value = mocked_reponse

        boleto.consulta_pdf("01234567891")

    patched_auth_request.assert_called_once()
    patched_get.assert_called_once()
