import re
from bs4 import BeautifulSoup
import requests
import json
from TimeHandler import *
from datetime import timedelta
import re

class YahooParser:
    def __init__(self):
        self.num_stocks_per_req = 40

    def _get_json_obj(self,data):
        return json.loads(data)

    def _prepare_txt_to_numeric(self, txt):
        """
        Convert shortent text representation of a number to float
        ie: 720M -> 720000000
        :param txt: shortent text representation of a number that is needed to be converted
        :return: a float number
        """
        txt = txt.upper()

        formats = {"M":1000000, "B":1000000000}

        try:
            for chr in formats.keys():
                pos = txt.find(chr)
                if pos >-1:
                    return float(txt[:pos]) * formats[chr]
        except:
            raise Exception("Error: can't convert {0} to a number representaiton, probably unknown format".format(txt))

        raise Exception("Error: can't convert {0} to a number representaiton, probably unknown format".format(txt))





    def _scrape_yql(self, quote_list, yql_table ,required_date):
        """
            Returns a dictionary where keys are stock symbols and keys are stock prices for required_date
            OR 0 if an error occurred
        """
        if len(quote_list)==1:
            quote_list_str = str(tuple(quote_list))[:-2]+')'
        else:
            quote_list_str = str(tuple(quote_list))

        try:
            # get the friday's data if required date happens to be weekend
            while required_date.isoweekday() in (6, 7):
                # timedelta(1) equals to 1 day
                required_date -= timedelta(1)

            # Date format used for yql : "YYYY-MM-DD" also called isoformat
            required_date_str = required_date.isoformat()
        except Exception as e:
            print("Exception caught while getting required_date string with error:, ", e)

        base_query = "http://query.yahooapis.com/v1/public/yql?q=select * from yahoo.finance."+yql_table+" where " \
                     "symbol in" + quote_list_str + " and startDate ='" + required_date_str + "' and endDate = " \
                                                                                              "'" + required_date_str + "'&env=store://datatables.org/alltableswithkeys&format=json"
        try:
            r = requests.get(base_query)
            jo = self._get_json_obj(r.text)
        except Exception as e:
            print("Exception Caught at Yahoo_Parser at requests.get(), ",e)
        output={}

        try:
            if len(quote_list) > 1:
                for i in jo["query"]["results"]['quote']:
                    output[i['Symbol']] = float(i['Close'])
            else:
                output[jo["query"]["results"]['quote']['Symbol']] = float(jo["query"]["results"]["quote"]["Close"])
        except Exception as e:
            print("Exception Caught: ", e)
        return output


    def scrape(self, param, quote, page,required_dates=None):
        """
        :param param: stock information to scrape
        :param quote: quote's symbol
        :param page is a financial statement page or price  ("bs","is","cf","price")
        :param required_date:array of date objects(used primarily for prices);default is None to get all dates available
        :return:  array with:
                    [
                        {"date1":value1},
                        {"date2":value2}
                    ]
        If param doesn't require date then return is:
                {"" :value1}
        """
        param=param.lower()
        page = page.lower()
        try:
            if page == "cf":
                url = "http://finance.yahoo.com/q/cf?s={0}".format(quote)
                return self._scrape(url,param)
            elif page == "bs":
                url = "http://finance.yahoo.com/q/bs?s={0}".format(quote)
                return self._scrape(url,param)
            elif page == "is":
                url = "http://finance.yahoo.com/q/is?s={0}".format(quote)
                return self._scrape(url,param)
            elif page == "ks":
                url = "http://finance.yahoo.com/q/ks?s={0}".format(quote)
                return self._scrape(url,param)
            elif page == "price":
                if len(required_dates) > 0:
                    return self._scrape_yql([quote],required_date=required_dates[0],yql_table="historicaldata")
                else:
                    raise Exception("Error: date is required for price for quote: {0}".format(quote))
            elif page == "dividends":
                if len(required_dates) > 0:
                    return self._scrape_yql([quote],required_date=required_dates[0], yql_table="dividendhistory")
            else:
                raise Exception("Exception: "+param+" is not supported")
        except Exception as e:
            print("Error while scraping for {0} with error: {1}".format(param, e))


    def _scrape(self, url, param):
        try:
            r=requests.get(url)
        except Exception as e:
            print("Exception: scraping {0} with error: {1}".format(param, e))

        data=r.text
        soup=BeautifulSoup(data)

        data=[]
        dates=[]
        try:
            #param_tag is the tag that has param as a text
            #re.I paramater tells regex to search in case-insensitive mode
            param_tag = soup.find(text = re.compile(param, re.I))
            if param_tag is not None:
                data = [sibling.text.strip().replace(",","") for sibling in param_tag.parent.parent.next_siblings]



            dates_td_tag = soup.find(text = re.compile("Period Ending"))
            if dates_td_tag is not None:
                dates = [sibling.text.strip().replace(",","") for sibling in dates_td_tag.parent.parent.parent.next_siblings]

        except Exception as e:
            raise Exception("Exception Caught: no {0} information or wrong param, with error: {2}".format(param, e))

        #Regex used to remove '(',')' from numbers, since
        # negative values are placed inside '(', ')'
        #we want negatives to be in format '-value' to be used in calculations
        regex = re.compile('[(-,)]')
        for i in range(0, len(data)):
            neg = False
            if '(' in data[i]:
                neg =True
            data[i]=regex.sub('', str(data[i]))
            data[i] = self._prepare_txt_to_numeric(data[i])

            if neg:
                data[i] *= -1


        if len(dates)==0 and len(data) == 1:
            return {"":data[0]}
        elif len(dates)==0 and len(data) >1:
            raise Exception("Error: there are two data points and no dates found for them while scraping for {0} ".format(param))
        else:
            return dict(zip(dates, data))


    def scrape_total_cashflow(self, quote):
        """
            Receives quote to get Total Cash Flow From Operating Activities
            from Yahoo

            Returns Dictionary with keys as dates and values as actual data
            Usually would return 4 elements for 4 previous quarters
        """
        #
        # DON'T USE THIS FUNCTION AS IT'S GOING TO GET REMOVED IN FUTURE VERSIONS
        #
        return self.scrape("Total Cash Flow From Operating Activities",quote,"cf")

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
        Convert shortent text representation of a number to float
        Also Check if txt is "-"(ie No data) and return "-" in that case
        ie: 720M -> 720000000
        :param txt: shortent text representation of a number that is needed to be converted
        :return: a string with a number
        """
        txt = txt.upper()

        if txt == "-":
            return txt


        formats = {"M":1000000, "B":1000000000}

        try:
            for chr in formats.keys():
                pos = txt.find(chr)
                if pos >-1:
                    return str (float(txt[:pos]) * formats[chr] )
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


    def scrape(self, quote_list, page, required_date = None):
        raise NotImplementedError("scrapemain is abstract, call its children classes")

    def scrape(self, quote, param, page, required_date = None):
        raise NotImplementedError("scrapemain is abstract, call its children classes")

    def scrape(self, quote_list, required_date):
        raise NotImplementedError("scrapemain is abstract, call its children classes")


class ScrapeYql(ScrapeMain):
    def __init__(self):
        self.names = {"dividendhistory":"Dividends", "historicaldata":"Close"}

    def prepare_url(self, quote_list, page, required_date):
        yql_table = page
        if len(quote_list)==1:
            quote_list_str = str(tuple(quote_list))[:-2]+')'
        else:
            quote_list_str = str(tuple(quote_list))

        try:
            # get the friday's data if required date happens to be weekend
            while required_date.isoweekday() in (6, 7):
                # timedelta(1) equals to 1 day
                required_date -= timedelta(1)
            # Date format used for yql : "YYYY-MM-DD" also called isoformat
            required_date_str = required_date.isoformat()
        except Exception as e:
            raise Exception("Exception caught while getting required_date string with error:, ", e)

        return "http://query.yahooapis.com/v1/public/yql?q=select * from yahoo.finance."+ yql_table +" where symbol in" + quote_list_str + " and startDate ='" + required_date_str + "' and endDate = '"+required_date_str\
              + "'&env=store://datatables.org/alltableswithkeys&format=json"

    def scrape(self, quote_list, required_date):
        raise NotImplementedError("not implemented in scrapeyql, should use children classes")


class ScrapeHistoricalPrices(ScrapeYql):
    #TODO:Implement
    pass

class ScrapeDividendHistory(ScrapeYql):
    def scrape(self, quote_list, required_date):
        tag_name = self.names["dividendhistory"]
        url = self.prepare_url(quote_list, "dividendhistory",required_date)
        r = self.get_request(url)
        jo = self.get_json_obj(r.text)

        output={}

        try:
            for i in jo["query"]["results"]['quote']:
                output[i['Symbol']] = float(i[tag_name])
        except Exception as e:
            print("Exception Caught: ", e)
        output["date"]= get_date_to_string(required_date)
        return output


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




