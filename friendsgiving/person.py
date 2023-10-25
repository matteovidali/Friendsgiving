from datetime import datetime, timezone, timedelta
from pathlib import Path
import json

class Person:
    def __init__(self, name, id=None, paid=0, owes={}, what_for={}):
        self.tz = timezone(-timedelta(hours=5))
        self.name = name
        self.id = name.lower() if id is None else id
        self.i_pay_file = Path(f'payfiles/{self.id}_pay_file')
        self.owes = owes
        self.total_out = 0
        self.what_for = what_for
        self.id_file = Path(f'id_file/{self.id}_id')
        self.get_or_set_self_id()

    def buys(self, item, value):
        with open(self.i_pay_file, "a+") as out_file:
            out_file.write(f"{self.name}, PAID: ${float(value):.2f}, For: {item}, Time: {datetime.now(tz=self.tz).strftime('%Y_%m_%d %H:%M:%S')}\n")

    def get_or_set_self_id(self):
        if not self.id_file.is_file():
            self.update()
            return 1
        with open(self.id_file) as jsonfile:
            s = json.load(jsonfile) 
            self.name = s['name']
            self.i_pay_file = Path(s['i_pay_file'])
            self.owes = s['owes']
            self.what_for = s['what_for']
            self.total_out = s['total_out']
    
    def pays(self, payee, amount, all=False):
        if all:
            self.owes[payee] = 0
        else:
            self.owes[payee] -= round(amount, 2)
        self.update()

    def update(self):
        with open(self.id_file, 'w+') as jsonfile:
            json.dump(self.asdict(), jsonfile)

    def asdict(self):
        return {'name': self.name, 
                'i_pay_file': str(self.i_pay_file), 
                'owes': self.owes, 
                'what_for': self.what_for, 
                'total_out':self.total_out}

def get_name_or_id(name_or_id: str,  ids: dict):
    name_or_id = name_or_id.lower()

    if name_or_id in [x.lower() for x in ids.values()]:
        for key, value in ids.items():
            if value.lower() == name_or_id:
                return key

    return ids[name_or_id]
