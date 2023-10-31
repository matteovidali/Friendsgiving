from datetime import datetime, timezone, timedelta
from pathlib import Path
import json

ids = {"156156": "Matteo", "252252": "Nia",
       "363363": "Grace", "454454": "Nick", 
       "545545": "Zoe", "656656": "Kye"}

def get_name_or_id(name_or_id: str, id: dict={}):
    global ids

    name_or_id = name_or_id.lower()

    if name_or_id in [x.lower() for x in ids.values()]:
        for key, value in ids.items():
            if value.lower() == name_or_id:
                return key

    return ids[name_or_id]

class Person:
    def __init__(self, name, id=None, paid=0, owes={}, what_for={}):
        self.name = name
        self.id = name.lower() if id is None else id
        self.tz = timezone(-timedelta(hours=5))
        self.i_pay_file = Path(f'payfiles/{self.id}_pay_file')
        self.owes = owes
        self.total_out = 0
        self.what_for = what_for
        self.id_file = Path(f'id_file/{self.id}_id')
        self.get_or_set_self_id()

    def buys(self, item, value):
        with open(self.i_pay_file, "a+") as out_file:
            out_file.write(f"{self.name}, PAID: ${float(value):.2f}, "
                           f"For: {item}, Time: {datetime.now(tz=self.tz).strftime('%Y_%m_%d %H:%M:%S')}\n")
        self.total_out += float(value)
        self.update()

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
            self.total_out = float(s['total_out'])
    
    def pays(self, payee, amount, all=False):
        amount = 0
        if all:
            amount = self.owes[payee]
            self.owes[payee] = 0
        else:
            amount = round(self.owes[payee] - float(amount), 2)
            self.owes[payee] = amount
        payee_name = get_name_or_id(payee)
        self.buys(f"Payed {payee_name}", amount)
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

