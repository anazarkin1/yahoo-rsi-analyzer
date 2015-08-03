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
        self.data = self.load_all()
        self.date_format_string="%b %d %Y"


    def save(self, param, stock, value):
        pass

    def load_all(self):
        with open(self.filename) as file:
            self.data = json.load(file)

            #check if file's content is valid json
            if type(self.data) != dict:
                self.data = {}

    def get(self, param, stock):
        """
        return date and value for param and stock.
        return None if there is not such param or stock
        :param param:
        :param stock:
        :return: {'Stock1': 'value1'}
        """
        if (param not in self.data) or (stock not in self.data[param]):
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
        date = get_date_to_string(date, format_string=self.date_format_string)

        if not param in self.data:
            self.data[param]={}
        if not stock in self.data[param]:
            self.data[param]={stock: {date: value}}

        self.data[param][stock][date]=value

    def save_to_disk(self):
        try:
            with open(self.filename, 'w') as file:
                file.write(json.dumps(self.data, file, indent = 4))
        except Exception as e:
            raise("***Error while saving new json data to disk, with error: {0}".format(e))












