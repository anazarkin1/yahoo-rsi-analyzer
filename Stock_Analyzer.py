from operator import itemgetter
import math

from TimeHandler import *

from Yahoo_Parser import *
from Json_Data_Manager import DataManager


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

    def _calculate_cashflow_growth(self, cashflow_info):
        """
            Receives cashflow_info - an object from scrape_total_cashflow(),
            that contains dates with corresponding cashflow values

            Formula to calculate performance:
            CF_growth= (CF_end- CF_start)/CF_start

        """
        output={}

        reverse=True
        sorted_dates = get_sorted_dates_array(cashflow_info.keys(), reverse)
        for i in range(0,len(sorted_dates)-1):
            try:
                # previous date actually is next one in the array since it's sorted in non-asc order
                str_date_start = get_date_to_string(sorted_dates[i+1])
                str_date_end = get_date_to_string(sorted_dates[i])

                if  float(cashflow_info[str_date_start]) != 0:
                    output[str_date_end]=round( ( float(cashflow_info[str_date_end]) - float(cashflow_info[
                                                                                               str_date_start]) ) /
                                                float(cashflow_info[str_date_start]), self.decimal_places )
                else:
                    output[str_date_end]=-9999999.9999
                    print("Exception caught while calculating cashflow growth, with error Division by 0")
            except Exception as e:
                print("Exception caught while calculating cashflow growth with error, ", e)


        return output


    def _calculate_cashflow_growth_all(self, quote_list, overwrite_file, cashflow_type="operating activities"):
        """
        Receives a list of quotes to scrape cashflow info on

        Returns dictionary with all quotes as keys and array of dictionaries, and for every
        dictonary inside this array keys are dates and values are growth_rates(basically just output from
            _calculate_cashflow_growth())
        """
        cashflow_type=cashflow_type.lower()

        output={}
        i=1
        for quote in quote_list:
            print(quote, i,"/",len(quote_list))
            i+=1
            try:
                file_info=self.dm.get_cashflow_all_dates(cashflow_type,quote)
                if overwrite_file==True:
                    cashflow_info = self.yp.scrape_total_cashflow(quote)

                    #save to json file
                    for date_str, value in cashflow_info.items():
                        date=get_string_to_date_object(date_str)
                        self.dm.save_cashflow_single(cashflow_type,quote,date,value)
                else:
                    cashflow_info = file_info
            except Exception as e:
                print('Exception caught while scraping total cashflow for ',quote,' with error' ,e)

            try:
                output[quote]=self._calculate_cashflow_growth(cashflow_info)
            except Exception as e:
                print('Exception caught while calculating cashflow growth() for ', quote, ' with error: ',e)

        return output
    def get_best_cashflow_performers_consec_periods(self, best_percentage, numb_consec_periods, overwrite_file):
        """
            Receives best_percentage = (100-percentage*100) % of other NYSE stocks a
            stock has to outperform,
            num_consec_periods - number of LATEST consecutive periods that a stock must be
            top performer based on best_percentage

            Returns dict where keys are symbols and values are dicts with
                keys as period and value as growth rate.
            Those symbols are for companies that have been best_percentage top in
            number of latest consecutive periods

        """

        # updates class's number of periods to analyze:
        self.num_periods_toanalyze_cashflow = int(numb_consec_periods)
        best_percentage=float(best_percentage)

        try:
            periods=self.get_best_cashflow_performers_by_period(best_percentage=best_percentage,overwrite_file= overwrite_file)
        except Exception as e:
            print("Exception caught get_best_cashflow_performers_consec_periods() while \
             performing get_best_cashflow_performers_by_period(), with error :", e)


        # array contains potential candidates for being returned as best
        # performers in consecutive periods,
        # we want to consider growth rates starting from the latest
        candidate_symbols_array=[]
        try:
            # periods are sorted in decreasing order accroding to the date
            last_period = periods[0]
            for data in last_period:
                candidate_symbols_array.append(data["Symbol"])
        except Exception as e:
            print("Exception caught while creating candidate_symbols_array, with error ", e)

        # get latest 'self.num_periods_toanalyze_cashflow' count periods
        try:
            for period in periods[1:self.num_periods_toanalyze_cashflow]:
                # get current period's best performers' symbols
                # to check if those symbols are in candidates array ie:
                # they are also best performers in previous consecutive periods
                cur_period_top_symbols_array=[]
                for i in period:
                    cur_period_top_symbols_array.append(i["Symbol"])

                # if one of the candidate symbols is not included in current period,
                # then it can't be recorded as top performer in consecutive periods

                # I use additional array since I'll be removing elements from the original array
                # and for loop won't be correct otherwise
                tmp_candidate_list=candidate_symbols_array[:]
                for symbol in tmp_candidate_list:
                    if symbol not in cur_period_top_symbols_array:
                        candidate_symbols_array.remove(symbol)
        except Exception as e:
            print("Exception caught while figuring out what companies are top in consecutive periods with error, ", e)

        return candidate_symbols_array
    def get_best_cashflow_performers_by_period(self,overwrite_file, best_percentage=.3, all_cashflow_data=None):
        """
            Receives best_percentage = (100-percentage*100) % of other NYSE stocks a
            stock has to outperform

            Returns an array with index representing periods(1 period is the earliest period data is for, .length is the latest one)
            Each array value is another array with values as dictionaries of structure: {Symbol,Cashflow_growth}. This inner array
            is sorted by cashflow_growth for each period in desc order and contains only (best_percentage*100) % top performers

            By period means that return array has indecies that represent periods,
            If want to get best performeres by cashflow growth for number of
            consecutive periods call get_best_cashflow_performers_consec_periods()
        """

        stock_list_to_work = self.stock_list[:]

        # array of dicts, each dict's keys are quotes and values are growth for this quote for this period,
        # array's indecies correspond to periods for which growths are calculated
        periods=[]

        try:
            if all_cashflow_data is None:
                all_cashflow_data =self._calculate_cashflow_growth_all(stock_list_to_work, overwrite_file=overwrite_file)
        except Exception as e:
            print("Exception caught at _calculate_cashflow_growth_all with error :", e)

        # loop through every period and for each period loop through all
        # companies to get their performance (dict {symb:performance}) into periods[i],
        # where i is i-th period we loop through
        try:
            symbols=all_cashflow_data.keys()
            for i in range(0,self.num_periods_toanalyze_cashflow):
                periods.append([])

            for symbol in symbols:
                reverse = True
                # sorted dates in decreasing order
                sorted_dates=get_sorted_dates_array(all_cashflow_data[symbol].keys(), reverse)
                if len(sorted_dates) < 2:
                    print("***Less than 2 dates for ", symbol)
                    continue

                num_periods=0
                if self.num_periods_toanalyze_cashflow<len(sorted_dates):
                    num_periods=self.num_periods_toanalyze_cashflow
                else:
                    num_periods=len(sorted_dates)
                for i in range(0, num_periods):
                    str_date=get_date_to_string(sorted_dates[i])
                    value_for_date = all_cashflow_data[symbol][str_date]
                    periods[i].append({"Symbol":symbol, "Cashflow_growth":value_for_date, "Date_reported":str_date})

        except Exception as e:
            print("Exception caught at get_best_cashflow_performers_by_period() while combining companies performancies into periods array, with error: ", e)


        # sort each period's array by dict's value
        try:
            for i in range (0, len(periods)):
                # print("\nBEFORE\n",periods[i])
                cut_number = math.ceil( len(periods[i])*best_percentage )
                periods[i]= sorted( periods[i], key=itemgetter('Cashflow_growth'), reverse=True)[:cut_number]
                # print("\nAFTER\n",periods[i])
                # only save best_percentage*100% of top performers for each period
        except Exception as e:
            print("Exception caught at _calculate_cashflow_growth_all() performing periods sort with cutting off worst performers, with error: ", e)
        # print("PERIODS: *********************\n", periods, "\n***********************************\n")
        return periods

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

                        output[stock][date_end] = round( (value_end - value_start) / value_start, self.decimal_places)
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
            if len(i) > 0:
                maxi = len(i)

        periods = [{} for i in range(0, maxi - 1)]

        for stock_name in data.keys():

            i = 0
            for period in data[stock_name].keys():
                periods[i][stock_name] = data[stock_name][period]
                i += 1

        return periods



    def _calculate_price_growth_all(self, quote_list, force_overwrite):

        output={}

        req_date =datetime(2014,3,28)
        return self.yp.scrape_stock_price(quote_list, req_date)

    def get_best_prices_performers_by_period(self, overwrite,  best_percentage=.3,all_price_data=None):
        stock_list_to_work=self.stock_list[:100]
        periods=[]
        try:
            if all_price_data is None:
                all_price_data=self._calculate_price_growth_all(stock_list_to_work, force_overwrite=overwrite)
        except Exception as e:
            print("Exception, at _calculate_prices_growth_all, with error:",e)

        try:
            symbols=all_price_data.keys()
            for i in range(0,self.num_periods_toanalyze_prices):
                periods.append([])

            for symbol in symbols:
                reverse=True

                sorted_dates=get_sorted_dates_array(all_price_data[symbol].keys(),reverse)
                if len(sorted_dates) < 2:
                    print("***Less than 2 dates for ", symbol, ". Cannot analyze.")
                    continue

                num_periods=0
                if self.num_periods_toanalyze_prices<len(sorted_dates):
                    num_periods=self.num_periods_toanalyze_prices
                else:
                    num_periods=len(sorted_dates)

                for i in range(0,num_periods):
                    str_date=get_date_to_string(sorted_dates[i])
                    value_for_date=all_price_data[symbol][str_date]
                    periods[i].append({"stock":symbol, "price_growth":value_for_date, "date_reported":str_date})
        except Exception as e:
            print("Exception, at get_best_prices_performers_by_period() while combining companies' performances into "
                  "periods array, with error:",e)

        try:
            for i in range(0, len(periods)):
                cut_number=math.ceil(len(periods[i])*best_percentage)
                periods[i]=sorted( periods[i], key=itemgetter('price_growth'), reverse=True )[:cut_number]
        except Exception as e:
            print("Exception, at _calculate_prices_growth_all() performing periods sort with cutting off worst "
                  "performers, with error:",e)

    def get_best_prices_performers_consec_periods(self,best_percentage,numb_consec_periods, overwrite):
        self.num_periods_toanalyze_prices=numb_consec_periods

        try:
            periods=self.get_best_prices_performers_by_period(overwrite=overwrite,best_percentage=best_percentage)
        except Exception as e:
            print("Exception, get_best_prices_performers_by_periods() with error:", e)

        return

    def _calculate_price_growth(self,price_info):
        output={}
        reverse=True

        sorted_dates=get_sorted_dates_array(price_info.keys(),reverse)
        for i in range(0,len(sorted_dates)-1):
            try:
                str_date_start=get_date_to_string(sorted_dates[i+1])
                str_date_end=get_date_to_string(sorted_dates[i])

                if float(price_info[str_date_start]) !=0:
                    output[str_date_end]=round ( (float(price_info[str_date_end])-float(price_info[str_date_start]))
                                                       /price_info[str_date_start],self.decimal_places)
                else:
                    output[str_date_end]=-99999999.999
                    print("Exception, calculating price growth with error: division by 0")
            except Exception as e:
                print("Exception, while caulculating price growth with error:",e)






