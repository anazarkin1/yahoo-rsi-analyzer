from Stock_Analyzer import StockAnalyzer
from TimeHandler import *
from JsonDataManager import DataManager
from Console import Console
from Yahoo_Parser import *
from datetime import *
def main():
    yp = ScrapeYahooKS()
    sa = StockAnalyzer()
    dm = DataManager()
    console=Console()
    # print( yp.scrape_total_cashflow("AAPL", "2015-01-01"))
    # print(yp.scrape_stock_price(["AAPL", "T"], "2010-11-11"))
    try:
        #testings:
        print( sa.mps(0.3,3, 6, "Total Cash Flows From Investing Activities", "cf",interval=30, force_download=True) )
        # while True:
        #     console.print("To exit type 'exit'")
        #     console.print("Type number from below:")
        #     console.print("1) Get best cashflow performers (best percentage, number of periods, force update)")
        #     console.print("2) Get best price performers (best percentage, number of periods, force update)")
        #     console.print("3) Get best price and cashflow performers (best percentage, number of periods, "
        #                   "force update)")
        #     choice = console.ask_value(">>")
        #     if choice=='exit':
        #         return
        #     elif choice=='1':
        #         best_percentage=console.ask_value("best percentage:")
        #         numb_periods=console.ask_value("number of periods:")
        #         force_update_tmp=console.ask_value("force update (y/n):")
        #
        #         if force_update_tmp=='y':
        #             force_update=True
        #         else:
        #             force_update=False
        #
        #         console.print("Calculating...")
        #         console.pprint(sa.get_best_cashflow_performers_consec_periods(best_percentage,
        #                                                                                  numb_periods,force_update) )
        #     elif choice=='2':
        #         best_percentage=console.ask_value("best percentage:")
        #         numb_periods=console.ask_value("number of periods:")
        #         force_update_tmp=console.ask_value("force update (y/n):")
        #
        #         if force_update_tmp=='y':
        #             force_update=True
        #         else:
        #             force_update=False
        #
        #         console.print("Calculating...")
        #         console.print("Result:\n")
        #         console.pprint(sa.get_best_prices_performers_consec_periods(best_percentage,
        #                                                                                  numb_periods,force_update) )
        #
        #     elif choice=='3':
        #         console.print("Not yet implemented")
        #     else:
        #         console.print("Wrong argument, try again")
        #
        #
        # # print(sa.get_best_cashflow_performers_consec_periods(0.3, 3, overwrite_file=True))
        #
        # print( sa.get_best_prices_performers_consec_periods(0.3,9, overwrite=True) )
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
