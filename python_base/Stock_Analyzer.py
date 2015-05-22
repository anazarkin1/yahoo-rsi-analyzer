import os
import sys
from Yahoo_Parser import YahooParser
from operator import itemgetter
import math

# used to sort dates
from datetime import datetime

class StockAnalyzer:
    def __init__(self, nyse_stock_list_file="nyse_stock_list.txt"):
        self.stock_list=[]
        self.load_nyse_stock_list(nyse_stock_list_file)
        self.decimal_places=4
        self.yp = YahooParser()

        # number of cash flow data quarters to compare every stock for
        self.num_periods_toanalyze_cashflow=3

    def get_string_to_date_object(self, str_to_parse, format_string="%b %d %Y"):
        return datetime.strptime(str_to_parse, format_string)

    def get_sorted_dates_array(self, array_to_sort, reverse=False):
        dates_to_sort=[]
        for date_to_sort in array_to_sort:
            dates_to_sort.append(self.get_string_to_date_object(date_to_sort))
        return sorted(dates_to_sort, reverse=reverse)

    def get_date_to_string(self, time_object, format_string="%b %d %Y"):
        # NOTE: Yahoo uses dates in format "Dec 1 2012", not "Dec 01 2012"
        # that's why we replace ' 0' with ' '
        return time_object.strftime(format_string).replace(' 0', ' ')

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
            CF_growth= (CF_current - CF_previous)/CF_current

        """
        output={}
        # Sorted dates in non-decr order
        reverse=False
        sorted_dates = self.get_sorted_dates_array(cashflow_info.keys(), reverse)
        for i in range(1,len(sorted_dates)):
            try:
                str_date_prev = self.get_date_to_string(sorted_dates[i-1])
                str_date_cur = self.get_date_to_string(sorted_dates[i])
                if  float(cashflow_info[str_date_cur]) != 0:
                    output[str_date_cur]=round( ( float(cashflow_info[str_date_cur]) - float(cashflow_info[str_date_prev]) ) / float(cashflow_info[str_date_cur]), self.decimal_places )
                else:
                    output[str_date_cur]=-9999999.9999
                    print("Exception caught while calculating cashflow growth, with error Division by 0")
            except Exception as e:
                print("Exception caught while calculating cashflow growth with error, ", e)


        return output

    def _calculate_cashflow_growth_all(self, quote_list):
        """
        Receives a list of quotes to scrape cashflow info on

        Returns dictionary with all quotes as keys and array of dictionaries, and for every
        dictonary inside this array keys are dates and values are growth_rates(basically just output from
            _calculate_cashflow_growth())
        """

        output={}
        i=1
        for quote in quote_list:
            print(quote, i,"/",len(quote_list))
            i+=1
            try:
                cashflow_info = self.yp.scrape_total_cashflow(quote)
            except Exception as e:
                print('Exception caught while scraping total cashflow for ',quote,' with error' ,e)

            try:
                output[quote]=self._calculate_cashflow_growth(cashflow_info)
            except Exception as e:
                print('Exception caught while calculating cashflow growth() for ', quote, ' with error: ',e)

        return output
    def get_best_cashflow_performers_consec_periods(self, best_percentage, numb_consec_periods):
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
        self.num_periods_toanalyze_cashflow = numb_consec_periods

        try:
            periods=self.get_best_cashflow_performers_by_period(best_percentage)
        except:
            print("Exception caught get_best_cashflow_performers_consec_periods() while \
             performing get_best_cashflow_performers_by_period(), with error :", e)


        # array contains potential candidates for being returned as best
        # performers in consecutive periods,
        # we want to consider growth rates starting from the latest
        candidate_symbols_array=[]
        try:
            last_period = periods[-1]
            for data in last_period:
                candidate_symbols_array.append(data["Symbol"])
        except Exception as e:
            print("Exception caught while creating candidate_symbols_array, with error ", e)

        #  print(periods)
        print('***** candidates: \n',candidate_symbols_array,'\n')

        # get latest 'self.num_periods_toanalyze_cashflow' count periods
        try:
            for period in periods[(-self.num_periods_toanalyze_cashflow):]:
                # get current period's best performers' symbols
                # to check if those symbols are in candidates array ie:
                # they are also best performers in previous consecutive periods
                cur_period_top_symbols_array=[]
                for i in period:
                    cur_period_top_symbols_array.append(i["Symbol"])

                # if one of the candidate symbols is not included in current period,
                # then it can't be recorded as top performer in consecutive periods
                for symbol in candidate_symbols_array:
                    if symbol not in cur_period_top_symbols_array:
                        candidate_symbols_array.remove(symbol)
        except Exception as e:
            print("Exception caught while figuring out what companies are top in consecutive periods with error, ", e)

        return candidate_symbols_array




    def get_best_cashflow_performers_by_period(self,best_percentage=.3, all_cashflow_data=None):
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
        stock_list_to_work=self.stock_list[:10]

        # array of dicts, each dict's keys are quotes and values are growth for this quote for this period,
        # array's indecies correspond to periods for which growths are calculated
        periods=[]

        try:
            if all_cashflow_data==None:
                all_cashflow_data =self._calculate_cashflow_growth_all(stock_list_to_work)
        except Exception as e:
            print("Exception caught at _calculate_cashflow_growth_all with error :", e)
        #  print("******All_cashflow_data\n", all_cashflow_data,'\n********\n')
        # loop through every period and for each period loop through all
        # companies to get their performance (dict {symb:performance}) into periods[i],
        # where i is i-th period we loop through
        try:
            symbols=all_cashflow_data.keys()
            #  for i in range(0,self.num_periods_toanalyze_cashflow):
            #      periods.append([])
            #      for symbol in symbols:
            #          sorted_dates =self.get_sorted_dates_array(all_cashflow_data[symbol].keys())

            #          # Company has less than 2 data values so we can't compute growth rate
            #          # since one period requires 2 consecutive date's data
            #          if len(sorted_dates)<2:
            #              continue

            #          # Company has no data for this period
            #          if i>len(sorted_dates):
            #              continue

            #          str_date=self.get_date_to_string(sorted_dates[i])
            #          value_for_date =all_cashflow_data[symbol][str_date]
            #          periods[i].append({"Symbol":symbol, "Cashflow_growth": value_for_date, "Date_reported":str_date})
            for i in range(0,self.num_periods_toanalyze_cashflow):
                periods.append([])

            for symbol in symbols:
                sorted_dates=self.get_sorted_dates_array(all_cashflow_data[symbol].keys())
                if len(sorted_dates) < 2:
                    print("***Less than 2 dates for ", symbol)
                    continue
                for i in range(0, len(sorted_dates)):
                    str_date=self.get_date_to_string(sorted_dates[i])
                    value_for_date = all_cashflow_data[symbol][str_date]
                    periods[i].append({"Symbol":symbol, "Cashflow_growth":value_for_date, "Date_reported":str_date})








        except Exception as e:
            print("Exception caught at get_best_cashflow_performers_by_period() while combining companies performancies into periods array, with error: ", e)


        # sort each period's array by dict's value
        try:
            for i in range (0, len(periods)):
                print("\nBEFORE\n",periods[i])
                cut_number = math.ceil(len(periods[i])*best_percentage)
                periods[i]= sorted( periods[i], key=itemgetter('Cashflow_growth'), reverse=True )[:cut_number]
                print("\nAFTER\n",periods[i])
                # only save best_percentage*100% of top performers for each period
        except Exception as e:
            print("Exception caught at _calculate_cashflow_growth_all() performing periods sort with cutting off worst performers, with error: ", e)
        # print("PERIODS: *********************\n", periods, "\n***********************************\n")
        return periods












