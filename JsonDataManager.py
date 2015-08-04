import json
from TimeHandler import *
"""
{
    "param1": {
                "Stock1": {
                            "Date1": value1,
                            ...
                          },
                ...
              },
    ...
}
"""
class DataManager:
    def __init__(self):
        self.filename="Data/data.json"
        self.data = ""
        self.data = self.load_all()
        self.date_format_string="%b %d %Y"


    def load_all(self):
        try:
            f = open(self.filename, 'r+')
            self.data = json.load(f).copy()
            f.close()

        except FileNotFoundError:
            #file doesn't exist, create it
            f = open(self.filename, 'w')
            f.close()
        except Exception as e:
            print("Error: loading json data file, with error: {0}".format(e))

        #check if file's content is valid json
        if type(self.data) != dict:
            self.data = {}

        return self.data.copy()

    def get(self, param, stock):
        """
        return all  dates and values for param and stock.
        return None if there is not such param or stock
        :param param:
        :param stock:
        :return: {'Stock1': 'value1', ...}
        """

        if (self.data is None) or (param not in self.data) or (stock not in self.data[param]):
            return None

        return self.data[param][stock]

    def update(self, param, stock, date, value):
        """

        :param param: string
        :param stock: string
        :param date: datetime
        :param value: float
        :return:
        """

        value = float(value)
        try:
            date = get_date_to_string(date, format_string=self.date_format_string)
        except Exception as e:
            raise("Error while converting date to string in JsonDataManager update, with: {0}".format(e))

        if type(self.data) is not dict:
            self.data={}
        if param not in self.data:
            self.data[param]={}
        if stock not in self.data[param]:
            self.data[param]={stock: {date: value}}

        self.data[param][stock][date]=value

    def update(self, param, stock, str_data):
        """

        :param param:
        :param stock:
        :param str_data:
        :return:
        """
        if len(str_data) ==0:
            return

        if type(self.data) is not dict:
            self.data={}

        if param not in self.data:
            self.data[param]={}

        self.data[param][stock]= str_data


    def save_to_disk(self):
        try:
            with open(self.filename, 'w') as file:
                file.write(json.dumps(self.data, file, indent = 4))
        except Exception as e:
            raise("***Error while saving new json data to disk, with error: {0}".format(e))












