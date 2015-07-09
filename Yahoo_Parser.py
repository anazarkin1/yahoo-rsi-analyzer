import re
from bs4 import BeautifulSoup
import requests
import json
from TimeHandler import *
from datetime import timedelta
import re

class YahooParser:


class ScrapeMain():
    def get_json_obj(self,data):
        return json.loads(data)

    def get_request(self, url):

        try:
            r=requests.get(url)
        except Exception as e:
            print("Exception: scraping {0} with error: {1}".format(url, e))
        return r

    def get_soup(self, data):
        return BeautifulSoup(data)

    def prepare_txt_to_numeric(self, txt):
        """
        Convert shortent text representation of a number to just a number in a string format
        Also Check if txt is "-"(ie No data) and return "null" in that case
        ie: 720M -> 720000000
        :param txt: shortent text representation of a number that is needed to be converted
        :return: a string with a number
        """
        txt = txt.upper()

        if txt == "-":
            return 'null'

        formats = {"M": 1000000, "B": 1000000000}

        try:
            for chr in formats.keys():
                pos = txt.find(chr)
                if pos > -1:
                    return str(float(txt[:pos]) * formats[chr])
            return txt
        except:
            raise Exception("Error: can't convert {0} to a number representaiton, probably unknown format".format(txt))

    def changeNeg(self, data):
        regex = re.compile('[(-,)]')
        for i in range(0, len(data)):
            neg = False
            if '(' in data[i]:
                neg = True
            data[i] = regex.sub('', str(data[i]))
            data[i] = self.prepare_txt_to_numeric(data[i])

            if neg:
                data[i] = "-" + data[i]
        return data


class ScrapeYql(ScrapeMain):
    names = {"dividendhistory": "Dividends", "historicaldata": "Close"}

    def __init__(self):
        self.name = "None"

    def prepare_url(self, quote, page, required_date):
        yql_table = page

        try:
            # get the friday's data if required date happens to be weekend
            while required_date.isoweekday() in (6, 7):
                # timedelta(1) equals to 1 day
                required_date -= timedelta(1)
            # Date format used for yql : "YYYY-MM-DD" also called isoformat
            required_date_str = required_date.isoformat()
        except Exception as e:
            raise Exception("Exception caught while getting required_date string with error:, ", e)

        return "http://query.yahooapis.com/v1/public/yql?q=select * from yahoo.finance."+ yql_table +" where symbol ='" + quote + "' and startDate ='" + required_date_str + "' and endDate = '"+required_date_str\
              + "'&env=store://datatables.org/alltableswithkeys&format=json"

    def scrape(self, quote, required_date):
        tag_name = self.names[self.name]
        url = self.prepare_url(quote, self.name, required_date)
        r = self.get_request(url)
        jo = self.get_json_obj(r.text)
        date_str = get_date_to_string(required_date)
        output = {}

        try:
            if jo["query"]["count"] < 1:
                return {date_str: "null"}
            elif jo["query"]["count"] == 1:
                return {date_str: jo["query"]["results"]["quote"][tag_name]}
            else:
                for i in jo["query"]["results"]['quote']:
                    output[i['Symbol']] =i[tag_name]
        except Exception as e:
            print("Exception Caught: ", e)
        output["date"]= date_str
        return output


class ScrapeHistoricalPrices(ScrapeYql):
    def __init__(self):
        self.name = "historicaldata"


class ScrapeDividendHistory(ScrapeYql):
    def __init__(self):
        self.name = "dividendhistory"


class ScrapeYahoo(ScrapeMain):
    def prepare_url(self, page, quote):
        return "http://finance.yahoo.com/q/{0}?s={1}".format(page, quote)

    def scrape(self, quote, param):
        page = self.page
        url = self.prepare_url(page, quote)
        r = self.get_request(url)
        soup = self.get_soup(r.text)

        data = []
        dates = []

        param_tag = soup.find(text = re.compile(param, re.I))
        if param_tag is not None:
            # if it's bolded text, it's in <strong></strong> tags, need to go one more level up the dom
            if param_tag.parent.name == "strong":
                data = [sib.text.strip().replace(",","") for sib in param_tag.parent.parent.next_siblings]
            else:
                data = [sib.text.strip().replace(",","") for sib in param_tag.parent.next_siblings]
        else:
            raise Exception("Error: no data found for {0} param {1}".format(quote, param))

        dates_tag = soup.find(text = re.compile("Period Ending"))
        if dates_tag is not None:
            dates = [sib.text.strip().replace(",","") for sib in dates_tag.parent.parent.parent.next_siblings]
        else:
            raise Exception("Error: no dates found for {0} param {1}".format(quote, param))

        try:
            data = self.changeNeg(data)
        except Exception as e:
            raise Exception("Error: converting data to numeric format, with error:{0}".format(e))
        return dict(zip(dates, data))


class ScrapeYahooKS(ScrapeYahoo):

    def __init__(self):
        self.page = "ks"

    def scrape(self, quote, param):
        page = self.page
        url = self.prepare_url(page, quote)
        r = self.get_request(url)
        soup = self.get_soup(r.text)

        data = None

        param_tag = soup.find(text = re.compile(param, re.I))
        if param_tag is not None:
            data = param_tag.parent.next_sibling.text.strip().replace(",","")
        else:
            raise Exception("Error: no data found for {0} param {1}".format(quote, param))

        try:
            data = self.changeNeg([data])[0]
        except Exception as e:
            raise Exception("Error: converting data to numeric format, with error:{0}".format(e))

        return {quote: data}


class ScrapeYahooBS(ScrapeYahoo):
    def __init__(self):
        self.page = 'bs'


class ScrapeYahooCF(ScrapeYahoo):
    def __init__(self):
        self.page = 'cf'


class ScrapeYahooIS(ScrapeYahoo):
    def __init__(self):
        self.page = 'is'




