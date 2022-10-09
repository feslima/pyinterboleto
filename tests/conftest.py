from pathlib import Path

import pytest
from dotenv import dotenv_values

from src.pyinterboleto import RequestConfigs

THIS_DIR = Path(__file__).resolve().parents[1]

CONFIGS = dotenv_values(THIS_DIR / "inter.env")


@pytest.fixture(scope="session")
def certificate_file():
    FILEPATH = THIS_DIR / "api_certificate.crt"
    FILEPATH.write_text(CONFIGS["INTER_API_CERTIFICATE"])

    yield FILEPATH

    FILEPATH.unlink(missing_ok=True)  # same as rm -f


@pytest.fixture(scope="session")
def key_file():
    FILEPATH = THIS_DIR / "api_key.key"
    FILEPATH.write_text(CONFIGS["INTER_API_KEY"])

    yield FILEPATH

    FILEPATH.unlink(missing_ok=True)  # same as rm -f


@pytest.fixture
def request_configs(certificate_file: Path, key_file: Path) -> RequestConfigs:
    acc: str = CONFIGS["INTER_ACC"]
    return RequestConfigs(conta_inter=acc, certificate=certificate_file, key=key_file)
