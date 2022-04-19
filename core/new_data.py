from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from decouple import config


def clean_str(text):
    """
    Limpa a string e transforma em formato numérico.
    """
    value = str(text).replace("\n", "").replace("\t", "")
    return value.replace(",", "")


def clean_usd_str(text):
    """
    Limpa a string USD e transforma em formato numérico.
    """
    value = str(text).replace("\n", "").replace("\t", "")
    return value.replace(".", "").replace(",", ".")


def search_for_previous_value(_dict, dict_prices, field_list):
    """
    Procura pelo dicionário do dia anterior
    para atualizar o dicionário quando existir valor não numérico.
    """
    previous_date = _dict["date"] + timedelta(days=-1)
    res = [x for x in dict_prices if x["date"] == previous_date][0]

    for field in field_list:
        _dict[field] = res[field]

    return _dict


def parse_date(date_str):
    """
    Recebe no padrão 01/Jan
    """
    _date = date_str.split("/")

    meses = {
        "Jan": "01",
        "Fev": "02",
        "Mar": "03",
        "Abr": "04",
        "Mai": "05",
        "Jun": "06",
        "Jul": "07",
        "Ago": "08",
        "Set": "09",
        "Out": "10",
        "Nov": "11",
        "Dez": "12"
    }

    ano = datetime.now().year
    data_frm_str = f"{_date[0]}/{meses[_date[1]]}/{str(ano)[2:]}"
    return datetime.strptime(data_frm_str, "%d/%m/%y")


def get_data_exchange():
    URL = config('LME_SOURCE')  # noqa E501
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="boxtabela")
    tabela = results.find("tbody")
    prices = tabela.find_all("tr")
    dict_prices = []

    for row in prices:
        row_data = row.find_all("td")
        data = row_data[0]
        cobre = row_data[1]
        zinco = row_data[2]
        aluminio = row_data[3]
        chumbo = row_data[4]
        estanho = row_data[5]
        niquel = row_data[6]
        dolar = row_data[7]

        data_str = clean_str(data.text)
        cobre_str = clean_str(cobre.text)
        zinco_str = clean_str(zinco.text)
        aluminio_str = clean_str(aluminio.text)
        chumbo_str = clean_str(chumbo.text)
        estanho_str = clean_str(estanho.text)
        niquel_str = clean_str(niquel.text)
        dolar_str = clean_usd_str(dolar.text)

        if data_str.startswith("Média") or data_str.startswith("Data"):
            pass
        else:
            _dict = {}
            _dict["date"] = parse_date(data_str)
            if dolar_str:
                _dict["dolar"] = dolar_str
            if cobre_str:
                _dict["cobre"] = cobre_str
            if chumbo_str:
                _dict["chumbo"] = chumbo_str
            if aluminio_str:
                _dict["aluminio"] = aluminio_str
            if estanho_str:
                _dict["estanho"] = estanho_str
            if niquel_str:
                _dict["niquel"] = niquel_str
            if zinco_str:
                _dict["zinco"] = zinco_str

            # Procura pelo campos sem valor numérico campo a campo.
            field_list = []
            for item in _dict.items():
                if item[1] == "Unofficial" or item[1] == "N/C" or item[1] == "feriado":
                    field_list.append(item[0])

            if "Unofficial" in _dict.values() or "N/C" in _dict.values() or "feriado" in _dict.values():
                pass
            else:
                dict_prices.append(_dict)

    return dict_prices
