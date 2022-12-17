import shutil
from pathlib import Path

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
