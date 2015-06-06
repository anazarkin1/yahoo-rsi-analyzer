import unittest
import sys
from math import floor
from datetime import datetime
#Used to import StockAnalyzer from parent folder
sys.path.append("..")
from Yahoo_Parser import YahooParser

class TestYahooParser(unittest.TestCase):
    def setUp(self):
        self.yp=YahooParser()



    def tearDown(self):
        pass

