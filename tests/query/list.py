from datetime import date, timedelta
from pprint import pprint
from typing import Dict, List, Tuple

import pytest
from pyinterboleto import Boleto, RequestConfigs
from pyinterboleto.consulta.lista import BoletoItem, OrdenarEnum
from tabulate import tabulate


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
