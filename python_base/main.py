from Stock_Analyzer import StockAnalyzer

def main():
    # yp = YahooParser()
    sa = StockAnalyzer()
    # print( yp.scrape_total_cashflow("AAPL", "2015-01-01"))
    # print(yp.scrape_stock_price(["AAPL", "T"], "2010-11-11"))
    try:
        print(sa.get_best_cashflow_performers_consec_periods(0.3, 3))
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
