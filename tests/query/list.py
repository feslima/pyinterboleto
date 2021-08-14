from datetime import date

import pytest
from pyinterboleto import Boleto, RequestConfigs
from pyinterboleto.consulta.lista import FiltrarEnum, OrdenarEnum


def ordering_naming(value) -> str:
    if isinstance(value, OrdenarEnum):
        return value.value

    return value


@pytest.mark.parametrize('enum', list(OrdenarEnum), ids=ordering_naming)
def test_ordering(request_configs: RequestConfigs, enum: OrdenarEnum):
    """I have no idea the criteria Inter uses to sort entries when the fields
    sorted have the same values. So, this acts as a smoke test for now."""
    boleto = Boleto(request_configs)

    today: date = date.today()

    year: int = today.year

    inicial = date(year, 1, 1)
    final = today

    default_list = boleto.consulta_lista(inicial, final)

    lista = boleto.consulta_lista(inicial, final, ordenar=enum)

    if enum == OrdenarEnum.NNA:
        assert default_list == lista
    else:
        assert default_list != lista


def filtering_naming(value) -> str:
    if isinstance(value, FiltrarEnum):
        return value.value

    return value


@pytest.mark.parametrize('enum', list(FiltrarEnum), ids=filtering_naming)
def test_filtering(request_configs: RequestConfigs, enum: FiltrarEnum):
    boleto = Boleto(request_configs)

    today: date = date.today()

    year: int = today.year

    inicial = date(year, 1, 1)
    final = today

    default_list = boleto.consulta_lista(inicial, final)
    lista = boleto.consulta_lista(inicial, final, filtrar=enum)

    if enum == FiltrarEnum.T:
        assert default_list == lista
    else:
        assert default_list != lista


@pytest.mark.parametrize('size', list(range(1, 8)))
def test_size(request_configs: RequestConfigs, size: int):
    boleto = Boleto(request_configs)

    today: date = date.today()

    year: int = today.year

    inicial = date(year, 1, 1)
    final = today

    lista = boleto.consulta_lista(inicial, final, size=size)

    assert lista.numberOfElements == size


@pytest.mark.skip(reason="Não há boletos emitidos suficiente para mais de 1 página")
def test_page_number():
    assert False
