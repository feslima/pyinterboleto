import pytest
from pyinterboleto import Boleto, RequestConfigs
from pyinterboleto.consulta.detalhado import BoletoDetail

ids = ('00677835839', '00678218266', '00678651490', '00678665391',
       '00684059480', '00699251197', '00710491624', '00710541303')


@pytest.mark.parametrize('number', ids)
def test_detailed(request_configs: RequestConfigs, number: str):
    """"Acts as smoke test. No real functionality to be tested besides the 
    dataclass creation and processing."""
    boleto = Boleto(request_configs)

    detail: BoletoDetail = boleto.consulta_detalhada(number)


@pytest.mark.parametrize('number', ids)
def test_pdf(request_configs: RequestConfigs, number: str):
    boleto = Boleto(request_configs)

    boleto.consulta_pdf(number)
