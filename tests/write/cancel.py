from unittest.mock import Mock, patch

from src.pyinterboleto.baixa import MotivoCancelamentoEnum
from src.pyinterboleto.boleto import Boleto
from src.pyinterboleto.utils.requests import RequestConfigs


def test_cancel(request_configs: RequestConfigs, patched_auth_request: Mock):
    boleto = Boleto(request_configs)
    with patch("src.pyinterboleto.baixa.post") as patched_post:
        mocked_reponse = Mock()
        mocked_reponse.status_code = 204
        patched_post.return_value = mocked_reponse

        boleto.cancelar_boleto("0012345689", MotivoCancelamentoEnum.A_PEDIDO_DO_CLIENTE)

    patched_auth_request.assert_called_once()
    patched_post.assert_called_once()
