from bs4 import BeautifulSoup
import requests
import json
import urllib.parse as urlparse
import os.path

FINECO_LOGIN_ENDPOINT = "https://finecobank.com/portalelogin"
FINECO_DASHBOARD = "https://finecobank.com/home/myfineco"
FINECO_PANIERI = "https://finecobank.com/mercati-e-trading/listini/analisi-lista"
FINECO_ANALISI = "https://finecobank.com/mercati-e-trading/analisi/analisi"
QUOTATIONS_FILE = "quotazioni.json"
RESULTS_FILE = "risultati.json"


class Fineco:
    __session = None

    __indexes = [
        "at_ftsemib",
        "at_midex",
        "at_cac",
        "at_dax",
        "at_dji",
        "at_ndx"
    ]

    __quotations = {

    }

    __cur_index_count = 1

    def __init__(self, session):
        if session is not None:
            self.__session = session

    def get_name(self):
        response = self.__session.get(FINECO_DASHBOARD)
        html = BeautifulSoup(response.text, "html.parser")
        header = html.find("div", class_="intestazione")
        if header is not None:
            return header.text.strip()
        return "-- NO --"

    def __get_all_quotations(self, index, page):
        quotations = []

        url = "%s?section=%s&page=%d" % (FINECO_PANIERI, index, page)

        print("[Page: %d] Enter in url %s" % (page, url))

        response = self.__session.get(url)
        html = BeautifulSoup(response.text, "html.parser")
        transactions_div = html.find("div", class_="transactions")
        if transactions_div is not None:
            quotation_table = transactions_div.find("table", class_="mts")
            if quotation_table is not None:
                if page is 0:
                    page_max_span = quotation_table.tfoot.find("div", id="paginazione").find("span", id="pag_max")
                    if page_max_span is not None:
                        self.__cur_index_count = int(page_max_span.text)
            for quotation_row in quotation_table.tbody.find_all('tr', recursive=False):
                a = quotation_row.find("a")
                if a is not None:
                    parsed = urlparse.urlparse(a.get('href'))

                    quotations.append({
                        "id": urlparse.parse_qs(parsed.query)['titolo'][0],
                        "link": a.get('href'),
                        "title": a.text
                    })

        return quotations

    def scan(self, save_in_file=False):
        for index in self.__indexes:
            self.__cur_index_count = 1
            self.__quotations[index] = self.__get_all_quotations(index, 0)
            if self.__cur_index_count is not 1:
                for cur_page in range(1, self.__cur_index_count):
                    self.__quotations[index] += self.__get_all_quotations(index, cur_page)

        if save_in_file:
            with open(QUOTATIONS_FILE, 'w') as outfile:
                json.dump(self.__quotations, outfile)
            print("Saved into file")

    def exists_quotation_file(self):
        return os.path.exists(QUOTATIONS_FILE)

    def capture_result(self, result=None):
        if result is None:
            result = ['Strong BUY', 'Strong SELL']
        results = ''
        with open(RESULTS_FILE) as json_file:
            data = json.load(json_file)
            for index in data:
                for quotation in data[index]:
                    if quotation.get('result') in result:
                        analys_url = "%s?titolo=%s" % (FINECO_ANALISI, quotation.get('id'))
                        results += ("Title %s (index: %s) collects a %s (%s)\n" % (
                            quotation.get('title'), index, quotation.get('result'), analys_url))

        return results

    def collect_data(self):
        results = {}
        with open(QUOTATION_FILE) as json_file:
            data = json.load(json_file)
            for index in data:
                results[index] = []
                for quotation in data[index]:
                    analys_url = "%s?titolo=%s" % (FINECO_ANALISI, quotation.get('id'))

                    print("Enter in Analysis Url for the title %s in index %s (%s)" % (
                        quotation.get('title'), index, analys_url))
                    response = self.__session.get(analys_url)

                    html = BeautifulSoup(response.text, "html.parser")
                    analys_div = html.find_all("div", class_="analisi-table")
                    if len(analys_div) > 0:
                        analys_table = analys_div[0].find("table", class_="details-table")
                        trs = analys_table.find_all("tr")
                        if len(trs) > 0:
                            tds = trs[0].find_all("td")
                            if len(tds) > 0:
                                result_part = quotation
                                result_part["result"] = tds[1].text.strip()
                                results[index].append(result_part)

        with open(RESULTS_FILE, 'w') as outfile:
            json.dump(results, outfile)

    @staticmethod
    def login(username, password):
        _session = requests.session()
        response = _session.post(FINECO_LOGIN_ENDPOINT, data={
            "LOGIN": username,
            "PASSWD": password
        })

        html = BeautifulSoup(response.text, "html.parser")

        if html.find("div", id='loginPage-box') is None:
            return Fineco(_session)
        return None
