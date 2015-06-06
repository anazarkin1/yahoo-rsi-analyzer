import json

class DataManager:
    def __init__(self):
        self._data_cashflow = ""

        # list of types of cashflow available from json file
        # ex: 'Operating Activities', 'Free',...
        self._cashflow_types = []

    def load_all_cashflow(self, filename="Data/cashflow.json"):
        try:
            with open(filename) as file:
                self._data_cashflow = json.load(file)
                return self.data_cashflow
        except Exception as e:
            print("Exception caught while loading cashflow.json with error:", e)
            return None
    
    @property
    def cashflow_types(self):
        return self.cashflow_types
