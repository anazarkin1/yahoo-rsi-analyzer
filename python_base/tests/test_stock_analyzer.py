import unittest
import sys
from math import floor
from datetime import datetime
#Used to import StockAnalyzer from parent folder
sys.path.append("..")
from Stock_Analyzer import StockAnalyzer

class TestStockAnalyzer(unittest.TestCase):
    def setUp(self):
        self.sa = StockAnalyzer()

    def test_get_date_to_string(self):
        r=self.sa.get_date_to_string(datetime(1994, 5, 20))
        e="May 20 1994"
        self.assertEqual(r,e)

    def test_get_string_to_date_object(self):
        #class datetime.datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)¶
        r=self.sa.get_string_to_date_object("May 20 1994")
        e=datetime(1994, 5, 20)
        self.assertEqual(r,e)


    def test_get_sorted_dates_array(self):
        reverse=False
        e=[]
        e.append(self.sa.get_string_to_date_object('Dec  11 2014'))
        e.append(self.sa.get_string_to_date_object('May 20 2014'))
        e.append(self.sa.get_string_to_date_object('May 21 2013'))
        e.append(self.sa.get_string_to_date_object('Apr 22 2013'))
        r = self.sa.get_sorted_dates_array(['May 21 2013', 'Dec 11 2014', 'Apr 22 2013', 'May 20 2014'], reverse)

        #Testing that they are in sorted order
        for i in range(1,len(r)):
            cur_date=r[i]
            prev_date=r[i-1]
            if reverse==True:
                self.assertTrue( cur_date<=prev_date )
            else:
                self.assertTrue( cur_date>=prev_date )

        #Testing that they consist from input dates
        for date in e:
            r.remove(date)
        self.assertTrue(len(r)==0)




    def test_calculate_cashflow_growth(self):
        #CF_growth= (CF_current - CF_previous)/CF_current

        ci={'May 20 2014': 10, 'Dec 11 2014': 50, 'May 11 2015' :60}
        r=self.sa._calculate_cashflow_growth(ci)
        print(r)
        self.assertEqual(r['May 11 2015'], .1667)
        self.assertEqual(r['Dec 11 2014'], .8)

        #Check that nothing else is calculated as we only have 2 periods
        #to report
        self.assertTrue(len(r)==2)
    def test_get_best_cashflow_performers_by_period(self):
        #all_cashflow_data
        acd={'LCM': {}, 'ACN': {'Aug 31 2014': 0.1734, 'Nov 30 2014': -0.8893, 'Feb 28 2015': -1.8972}, 'WUBA': {},
        'ABT': {'Dec 31 2014': 0.0299, 'Sep 30 2014': 0.2506, 'Mar 31 2015': -618.0}, 'AIR': {'Aug 31 2014': -3.2067, 'Nov 30 2014': 0.0625, 'Feb 28 2015': 0.2727},
        'AGC': {}, 'AYI': {'Aug 31 2014': 0.3154, 'Nov 30 2014': -1.2334, 'Feb 28 2015': -0.6215},
        'AHC': {'Dec 31 2014': 0.9908, 'Sep 30 2014': 0.9817, 'Mar 31 2015': -2.4659}, 'ATU': {'Aug 31 2014': 0.3025, 'May 31 2014': 0.8916, 'Nov 30 2014': -1.0721},
        'ASX': {}, 'MMM': {'Dec 31 2014': 0.2162, 'Sep 30 2014': 0.0415, 'Mar 31 2015': -1.0213}, 'AAV': {}, 'ACT^A': {'Dec 31 2014': 0.3565, 'Sep 30 2014': 0.1011, 'Mar 31 2015': -0.5459},
        'WMS': {'Oct 4 2014': -0.0896, 'Jul 12 2014': 0.6611, 'Jan 3 2015': -0.3025}, 'AVK': {}, 'ACW': {'Dec 31 2014': 0.7685, 'Sep 30 2014': -2.2386, 'Mar 31 2015': -1.3109}, 'AGRO': {},
        'ACT': {'Dec 31 2014': 0.3565, 'Sep 30 2014': 0.1011, 'Mar 31 2015': -0.5459}, 'GCH': {},
        'ACCO': {'Dec 31 2014': 0.406, 'Sep 30 2014': 0.315, 'Mar 31 2015': -1.0882}, 'AAP': {'Oct 4 2014': -0.0896, 'Jul 12 2014': 0.6611, 'Jan 3 2015': -0.3025}, 'ABB': {}, 'JEQ': {},
         'ADPT': {'Dec 31 2014': -2.6659, 'Sep 30 2014': 0.9822, 'Mar 31 2015': 0.6777}, 'WBAI': {}, 'ACE': {'Dec 31 2014': 0.1162, 'Sep 30 2014': 0.2487, 'Mar 31 2015': -0.1851},
         'ADT': {'Dec 26 2014': 0.0407, 'Mar 27 2015': 0.0465, 'Sep 26 2014': -0.1525}, 'ATV': {}, 'PEO': {}, 'AAN': {'Dec 31 2014': 0.5824, 'Sep 30 2014': -4.1883, 'Mar 31 2015': 0.8308},
          'ATEN': {'Dec 31 2014': 0.7765, 'Sep 30 2014': -0.7741, 'Mar 31 2015': -2.0951}, 'DDD': {'Dec 31 2014': 0.6309, 'Sep 30 2014': -1.2201, 'Mar 31 2015': -23.7737},
          'AAC': {'Dec 31 2014': -1.5986, 'Mar 31 2015': 0.1128}, 'SGF': {}, 'ANF': {'Jan 31 2015': 0.8099, 'Nov 1 2014': 0.7061, 'Aug 2 2014': -1.5389},
          'AKR': {'Dec 31 2014': 0.2473, 'Sep 30 2014': -0.5193, 'Mar 31 2015': 0.2172}, 'ADX': {}, 'ABM': {'Jan 31 2015': -0.966, 'Oct 31 2014': 0.697, 'Jul 31 2014': -2.9689},
           'ATE': {}, 'ABBV': {'Dec 31 2014': -2.09, 'Sep 30 2014': 0.0386, 'Mar 31 2015': 0.6353}}



    def tearDown(self):
        pass