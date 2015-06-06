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


    def tearDown(self):
        pass