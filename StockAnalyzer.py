from operator import itemgetter
import math

from TimeHandler import *

from YahooParser import *
from JsonDataManager import DataManager


from datetime import timedelta
# used to sort dates
from datetime import datetime


class StockAnalyzer:
    def __init__(self, nyse_stock_list_file="nyse_stock_list.txt"):
        self.stock_list=[]
        self.load_nyse_stock_list(nyse_stock_list_file)
        self.decimal_places=4
        self.dm = DataManager()



        # number of cash flow data quarters to compare every stock for
        self.num_periods_toanalyze_cashflow = 3

        #number of prices months to compare every stock for
        self.num_periods_toanalyze_prices = 8


    def load_nyse_stock_list(self, nyse_stock_list_file="nyse_stock_list.txt"):
        """
        Populate self.stocks_list with nyse stocks

        """

        with open(nyse_stock_list_file, newline="") as file:
            self.stock_list=[elem.replace('"',"").strip("\n") for elem in file]

    #new
    def _convert_str_data(self, str_data, date_format):
        """

        :param str_data: format:
                    {"date1":"value1", "date2":"value2",..}
        :return:
                    {date1: value1, date2: value2, ...}
                    dates are datetime objs, values are floats
        """
        output = {}
        for str_date, str_value in str_data.items():
            if str_value == "null":
                raise Exception("No value data available on date {0}".format(str_data))
            try:
                date = get_string_to_date_object(str_date, date_format)
            except Exception as e:
                raise Exception("Error converting string date {0} to datetime object".format(str_date))
            try:
                value = float(str_value)
            except Exception as e:
                raise Exception("Error converting string  value {0} to float bject".format(str_value))
            output[date] = value
        return output


    #new
    def mps(self, best_percentage, num_periods, num_periods_prices, param , page,interval=1,force_download=False):

        try:
            #days interval betweeen data points to analyze
            interval = int(interval)

            #instantiate a scraper according to page
            page = page.upper()
            scraper_class = globals()["ScrapeYahoo{0}".format(page)]
            scraper = scraper_class()


            param = str(param)
            param_data = {}
            counter = 1

            end_day = datetime(month=datetime.today().month -1, day=28, year=datetime.today().year)


            list_required_dates = [end_day]
            for i in range(1, num_periods_prices):
                list_required_dates.append(list_required_dates[-1] - timedelta(days= interval))

            for stock in self.stock_list[:]:
                print("Working on {0}, {1} / {2}".format(stock, counter, len(self.stock_list)) )
                try:
                    param_str_data={}

                    #only for params that are reported every day, that we get from yql
                    if param.lower() in {"historical prices", "dividend history"}:
                        param_str_data = scraper.scrape_list(stock, list_required_dates)

                    #params from the html parsing, reported quaterly
                    else:
                        param_str_data = self.dm.get(param, stock)
                        if force_download or (param_str_data is None):
                            param_str_data = scraper.scrape(stock, param)
                            # update json data manager's data object
                            self.dm.update(param, stock, param_str_data)

                except Exception as e:
                    print(e)

                try:
                    param_data[stock] = self._convert_str_data(param_str_data, date_format="%b %d %Y")
                except Exception as e:
                    print("Error while calculating mps on {0} for date {1}, with error: {2}".format(stock, param_str_data,e))
                counter += 1

            #save json data manager's data into a file, since updated all stocks
            self.dm.save_to_disk()

            growth_data = self._calculate_growth_all(param_data)
            periods_data = self._transform_to_periods(growth_data)
            param_best = self._get_best_consec_periods(periods_data, best_percentage, num_periods)

            print("{0} best: {1}".format(param, param_best))
            return param_best

        except Exception as e:
            print("Error: at mpsv1 with error: {0}".format(e))

    #new
    def _calculate_growth_all(self, data):
        """
        Calculates growth ratios for every stock in the input dict
        Could be used for calculation of growth ratios of any param as long as input data meets requirements

        Formula: growth = (end - start) / start
        :param data: format :{ "StockName1: {date1: value1, date2: value2, date3: value3},
                               "StockName2": {date2: value3 ,date4: value455}
                              }

        :return: { "StockName1": {date1: ratio1, date2:ratio2},
                   "StockName2": {date2: ratio2}
                    }
        #Note : All dates are datetime objects, All values and ratios are floats, All stocknames are strings

        """
        output = {}

        for stock in data.keys():
            try:
                #dates are sorted in non-ascending order
                dates = sorted(data[stock].keys(), reverse = True)
                for i in range(0, len(dates) - 1):
                    date_start = dates[i+1]
                    date_end = dates[i]
                    value_start = data[stock][date_start]
                    value_end = data[stock][date_end]

                    if value_start != 0:
                        #if the first time adding data to this stock, init it's content dict
                        if stock not in output.keys():
                            output[stock] = {}

                        output[stock][date_end] = round( (value_end - value_start) / abs(value_start), self.decimal_places)
                    else:
                        print("Error: division by zero at calculating growth for {0} on dates {1}, {2}".format(stock,str(date_end), str(date_start)) )
                        break;


            except Exception as e:
                print("Error: calculating growth for {0} stock, with error: {1}".format(stock, e))

        return output

    #new
    def _transform_to_periods(self, data):
        """

        :param data: output of _calculate_growth_all  format:
                     { "StockName1": {date1: ratio1, date2:ratio2},
                       "StockName2": {date2: ratio2, date33: ratio44}
                     }
                     Assumption: all ratios are valid floats, this function doesn't check correctness of ratios

        :param best_percentage:
        :param num_consec_periods:
        :return: from input example array of dictionaries for every time period ,
                    (keys are stocknames, values are their ratios for that period:
                    [
                         {"Stockname1":ratio2 , "Stockname2": ratio44} ,
                         {"Stockname1: ratio1, "Stockname2": ratio2}
                    ]

        """

        #find max number of periods in all stock dicts
        #used to init periods array with enough number of dicts
        maxi = 0
        for i in data.keys():
            if len(i) > maxi:
                maxi = len(i)

        periods = [{} for i in range(0, maxi)]

        for stock_name in data.keys():
            i = 0
            sorted_dates = get_sorted_dates_array(data[stock_name].keys(),reverse=True)
            for period in sorted_dates[:maxi]:
                periods[i][stock_name] = data[stock_name][period]
                i += 1

        return periods


    #new
    def _get_best_consec_periods(self, periods,  best_percentage, num_periods):
        """

        :param periods:
            format: [
                        {"SN1": ratio2, "SN2": ratio44},
                        {"SN1": ratio1, "SN2": ratio3},
                        ...
                    ]
        :param best_percentage:
        :param num_periods:
        :return:
        """
        # if len(periods) < num_periods:
        #     raise Exception("***Not enough periods data passed to calculate best consec periods, passed {0} need {1}".format(len(periods), num_periods))
        # else:
        #     num_periods = int(num_periods)
        best_percentage = float(best_percentage)

        candidates = [x[0] for x in sorted( periods[0].items(), key = itemgetter(1), reverse = True ) ]

        #only need best_percentage of them
        cut_number = math.ceil( len(candidates) * best_percentage )
        candidates = candidates[:cut_number]

        #for loop from 1 to num_periods-1 since first period's top are already included
        for i in range(1, num_periods):
            cut_number = math.ceil( len(periods[i]) * best_percentage )
            cur_period_candidates = [x[0] for x in sorted( periods[i].items(), key = itemgetter(1) , reverse = True )[:cut_number] ]

            old_candidates = candidates[:]
            for cand in old_candidates:
                if cand not in cur_period_candidates:
                    candidates.remove(cand)


        return candidates

