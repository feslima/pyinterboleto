from datetime import date
from unittest.mock import Mock, patch

from src.pyinterboleto import Boleto, RequestConfigs
from src.pyinterboleto.consulta.lista import SituacaoEnum
from tests.query.detail import get_mocked_detail_response


def get_mocked_list_response():
    return {
        "totalPages": 1,
        "totalElements": 4,
        "last": True,
        "first": True,
        "size": 100,
        "numberOfElements": 4,
        "content": [
            get_mocked_detail_response(),
            get_mocked_detail_response(),
            get_mocked_detail_response(),
            get_mocked_detail_response(),
        ],
    }


def test_get_list(request_configs: RequestConfigs, patched_auth_request: Mock):
    boleto = Boleto(request_configs)

    today: date = date.today()

    year: int = today.year

    inicial = date(year, 1, 1)
    final = today

    situacao = (SituacaoEnum.VENCIDO,)

    with patch("src.pyinterboleto.consulta.lista.get") as patched_get:
        mocked_reponse = Mock()
        mocked_reponse.status_code = 200
        mocked_reponse.json = Mock(return_value=get_mocked_list_response())
        patched_get.return_value = mocked_reponse

        result = boleto.consulta_lista(
            inicial, final, situacao=situacao, tipo_ordenacao="ASC"
        )

        assert result.totalPages == 1
        assert result.totalElements == 4

    patched_auth_request.assert_called_once()
    patched_get.assert_called_once()
