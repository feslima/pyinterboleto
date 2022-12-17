import shutil
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.pyinterboleto import RequestConfigs, ScopeEnum


@pytest.fixture
def cert_dir(tmp_path: Path):
    d = tmp_path / "certs"
    if d.exists():
        shutil.rmtree(str(d), ignore_errors=True)

    d.mkdir()

    yield d

    shutil.rmtree(str(d), ignore_errors=True)


@pytest.fixture
def certificate_file(cert_dir: Path):
    FILEPATH = cert_dir / "api_certificate.crt"
    FILEPATH.write_text("some invalid cerificate file contents")

    yield FILEPATH


@pytest.fixture
def key_file(cert_dir: Path):
    FILEPATH = cert_dir / "api_key.key"
    FILEPATH.write_text("some invalid key file contents")

    yield FILEPATH


@pytest.fixture
def request_configs(certificate_file: Path, key_file: Path) -> RequestConfigs:
    return RequestConfigs(
        client_id="some-client-id",
        client_secret="some-client-secret",
        certificate=certificate_file,
        scopes=ScopeEnum.get_all_scopes(),
        key=key_file,
    )


@pytest.fixture(name="patched_auth_request")
def patched_auth_fixture():
    with patch("src.pyinterboleto.auth.post") as patched_post:
        mocked_reponse = Mock()
        mocked_reponse.status_code = 200
        mocked_reponse.json = Mock(return_value={"access_token": "some-dummy-token"})
        patched_post.return_value = mocked_reponse

        yield patched_post
