import json
from TimeHandler import *
class DataManager:
    def __init__(self):
        self._data_cashflow = ""

        # list of types of cashflow available from json file
        # ex: 'operating Activities', 'free',...
        self._cashflow_types = []
        self.load_all_cashflow()

    def load_all_cashflow(self, filename="Data/cashflow.json"):
        try:
            with open(filename) as file:
                self._data_cashflow = json.load(file)

                if "cashflow" not in  self._data_cashflow.keys():
                    self._data_cashflow["cashflow"]={}

                self._cashflow_types=self._data_cashflow["cashflow"].keys()
                return self._data_cashflow
        except Exception as e:
            print("Exception caught while loading cashflow.json with error:", e)
            return None


    def get_cashflow_all_dates(self,cashflow_type, stock ):
        '''

        :param cashflow_type: a type of cashflow from self._cashflow_types
        :param stock: stock name
        :return: all available cashflow data of specified type from cashflow.json on this stock. Return None if nothing
        is available
        format: {"Date1":121324.1, "Date2":1256.9}
        '''

        try:
            if "cashflow" not in self._data_cashflow.keys() or cashflow_type not in self._data_cashflow[
                "cashflow"].keys or stock not in self._data_cashflow[cashflow][cashflow_type].keys():
                return None
            if len(self._data_cashflow["cashflow"][cashflow_type][stock])==0:
                return None
            return self._data_cashflow["cashflow"][cashflow_type][stock].copy()
        except Exception as e:
            print("Exception caught while getting cashflow data from json file for "+stock+" with error:",e)
            return None

    def save_cashflow_single(self,cashflow_type, stock, date, value, overwrite=True, filename="Data/cashflow.json"):
        '''

        :param cashflow_type:
        :param stock:
        :param date: datetime object
        :param value:
        :param overwrite:
        :return:
        '''

        cashflow_type=cashflow_type.lower()
        value=float(value)
        try:
            date_str=get_date_to_string(date)
        except Exception as e:
            print("Exception caught while converting date to string with error:", e)

        try:
            if cashflow_type not in self._cashflow_types:
                self._cashflow_types.append(cashflow_type)

            if "cashflow" not in self._data_cashflow.keys():
                self._data_cashflow["cashflow"]={}
            if cashflow_type not in self._data_cashflow["cashflow"].keys():
                self._data_cashflow["cashflow"][cashflow_type]={}

            if  stock not in self._data_cashflow["cashflow"][cashflow_type].keys():
                self._data_cashflow["cashflow"][cashflow_type][stock]={}

            if (date_str not in self._data_cashflow["cashflow"][cashflow_type][stock].keys() or overwrite):
                self._data_cashflow["cashflow"][cashflow_type][stock][date_str]=value
                with open(filename, 'w') as file:
                    file.write(json.dumps(self._data_cashflow,file, indent=4))

        except Exception as e:
            print ("Exception caught while saving single cashflow item for " +stock+" on date "+date_str+" with "
                                                                                                       "error:", e)
    @property
    def cashflow_types(self):
        return self.cashflow_types