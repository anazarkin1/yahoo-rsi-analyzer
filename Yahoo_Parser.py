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


    def scrape(self, param, quote, type ,required_dates=None):
        """
        :param param: stock information to scrape
        :param quote: quote's symbol
        :param type is a financial statement type or price  ("bs","is","cf","price")
        :param required_date:array of date objects(used primarily for prices);default is None to get all dates available
        :return:  array with:
                    [
                        {"date1":value1},
                        {"date2":value2}
                    ]
        """
        param=param.lower()
        type = type.lower()
        try:
            if type == "cf":
                url = "http://finance.yahoo.com/q/cf?s={0}".format(quote)
                return self._scrape(url,param)
            elif type == "bs":
                url = "http://finance.yahoo.com/q/bs?s={0}".format(quote)
                return self._scrape(url,param)
            elif type == "is":
                url = "http://finance.yahoo.com/q/is?s={0}".format(quote)
                return self._scrape(url,param)
            elif type == "ks":
                url = "http://finance.yahoo.com/q/ks?s={0}".format(quote)
                return self._scrape(url,param)

            elif type == "price":
                if len(required_dates) > 0:
                    return self._scrape_yql([quote],required_date=required_dates[0],yql_table="historicaldata")
                else:
                    raise Exception("Error: date is required for price for quote: {0}".format(quote))
            elif type == "dividends":
                if len(required_dates) > 0:
                    return self._scrape_yql([quote],required_date=required_dates[0], yql_table="dividendhistory")
            else:
                raise Exception("Exception: "+param+" is not supported yet")
        except Exception as e:
            print("Error while scraping for {0}".format(param))


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
            table = soup.find('table', attrs={'class': 'yfnc_tabledata1'})
            if table is None:
                raise Exception("Exception Caught: can't find table tr(Probably no {0} information)".format(param))
            trs = table.table.find_all('tr')
            # trs = [ele.text.strip().replace(",", "") for ele in trs_raw]
            for tr in trs:
                tds = tr.find_all('td')
                pos = 1
                for td in tds:
                    if td.text.strip().lower() == param:
                        data = [ele.text.strip().replace(",", "") for ele in tds[pos:]]
                    else:
                        pos += 1

            dates_td_tag = soup.find(text = re.compile("Period Ending"))
            dates = [sibling.text.strip().replace(",","") for sibling in dates_td_tag.parent.parent.parent.next_siblings]

        except Exception as e:
            raise Exception("Exception Caught: can't find table tr(Probably no {0} information) with error: {1}".format(param, e))

        #Regex used to remove '(',')' from cash flow numbers, since
        # negative values are placed inside '(', ')'
        #we want negatives to be in format '-value' to be used in calculations
        regex = re.compile('[(-,)]')
        for i in range(0, len(data)):
            neg = False
            if '(' in data[i]:
                neg =True
            data[i]=regex.sub('', str(data[i]))
            data[i] = float(data[i])

            if neg:
                data[i] *= -1


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

