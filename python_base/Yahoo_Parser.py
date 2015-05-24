import re

from bs4 import BeautifulSoup
import requests

#Using zip instead of izip since izip gives an error for some reason
#used for itertools.izip as it is said to be more memory efficient than zip
#http://stackoverflow.com/questions/209840/map-two-lists-into-a-dictionary-in-python
import json


class YahooParser:
    def __init__(self):
        pass

    def _get_json_obj(self,data):
        return json.loads(data)

    def scrape_stock_price(self, quote_list, required_date):
        """
            Returns a dictionary where keys are stock symbols and keys are stock prices for required_date
            OR 0 if an error occurred
        """
        if len(quote_list)==1:
            quote_list_str = str(tuple(quote_list))[:-2]+')'
        else:
            quote_list_str = str(tuple(quote_list))

        base_query= "http://query.yahooapis.com/v1/public/yql?q=select * from yahoo.finance.historicaldata where symbol in"+quote_list_str+" and startDate ='"+required_date+"' and endDate = '"+required_date+"'&env=store://datatables.org/alltableswithkeys&format=json"
        try:
            r = requests.get(base_query)
            jo = self._get_json_obj(r.text)
        except Exception as e:
            print("Exception Caught at Yahoo_Parser at requests.get(), ",e)
        output={}


        if len(quote_list)>1:
            for i in jo["query"]["results"]['quote']:
                try:
                    output[i['Symbol']]=float(i['Close'])
                except Exception as e:
                    print("Exception Caught: ", e)
        else:
            try:
                output[jo["query"]["results"]['quote']['Symbol']]=float(jo["query"]["results"]["quote"]["Close"])
            except Exception as e:
                print("Exception Caught: ", e)
        return output




    def scrape_total_cashflow(self, quote):
        """
            Receives quote to get Total Cash Flow From Operating Activities
            from Yahoo

            Returns Dictionary with keys as dates and values as actual data
            Usually would return 4 elements for 4 previous quarters
        """

        url="http://finance.yahoo.com/q/cf?s="+quote
        try:
            r = requests.get(url)
        except Exception as e:
            print("Exception Caught: scraping total cashflow for "+quote+" error:",e)

        data=r.text
        soup=BeautifulSoup(data)

        data=[]
        dates=[]
        try:
            table = soup.find('table', attrs={'class':'yfnc_tabledata1'})
            if table is None:
                raise ValueError("Exception Caught: can't find table tr(Probably no cashflow information) for " + quote)
            rows = table.find_all('tr')
        except Exception as e:
            raise ValueError("Exception Caught: can't find table tr(Probably no cashflow information) for "+quote+" error:",e)



        for row in rows:
            cols=row.find_all('td')
            cols = [ele.text.strip().replace(",","") for ele in cols]
            for col in cols:
                if col=="Total Cash Flow From Operating Activities":
                    data=cols[1:]
                if col=="Period Ending":
                    dates=cols[1:]


        #Regex used to remove '(',')' from cash flow numbers, since
        #some of them are presented in this way, ex: (3,911)
        regex = re.compile('[(-,)]')
        for i in range(0,len(data)):
            data[i]=regex.sub('', str(data[i]))

        return dict(zip(dates, data))
