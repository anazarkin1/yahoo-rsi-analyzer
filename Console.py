__author__ = 'alex'
from pprint import pprint
class Console:
    def __init__(self):
        pass

    def print(self, str):
        print(str)

    def pprint(self,obj):
        pprint(obj)

    def ask_value(self,message):
        return input(message+"\n")

