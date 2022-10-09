from pathlib import Path
from unittest.mock import Mock, patch
from uuid import uuid4

from src.pyinterboleto.auth import build_auth_body, get_auth_token
from src.pyinterboleto.utils.requests import RequestConfigs, ScopeEnum


def test_payload_builder():
    c_id = uuid4()
    c_secret = uuid4()
    scopes = (ScopeEnum.EXTRATO_READ, ScopeEnum.BOLETO_COBRANCA_READ)
    body = build_auth_body(str(c_id), str(c_secret), scopes)
    expected_string = (
        f"client_id={c_id}&client_secret={c_secret}"
        "&scope=extrato.read boleto-cobranca.read&grant_type=client_credentials"
    )
    assert body == expected_string


def test_auth_request_works():
    c_id = uuid4()
    c_secret = uuid4()
    scopes = (ScopeEnum.EXTRATO_READ, ScopeEnum.BOLETO_COBRANCA_READ)
    cert = Path(__file__).resolve()
    key = Path(__file__).resolve()
    configs = RequestConfigs(
        client_id=str(c_id),
        client_secret=str(c_secret),
        scopes=scopes,
        certificate=cert,
        key=key,
    )
    expected_token_value = "some-dummy-token"

    with patch("src.pyinterboleto.auth.post") as patched_post:
        mocked_reponse = Mock()
        mocked_reponse.status_code = 200
        mocked_reponse.json = Mock(return_value={"access_token": expected_token_value})
        patched_post.return_value = mocked_reponse

        token = get_auth_token(configs)

    patched_post.assert_called_once()
    assert token == expected_token_value
