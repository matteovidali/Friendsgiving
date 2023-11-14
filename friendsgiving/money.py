from dataclasses import dataclass
from pathlib import Path, FileExistsError
from datetime import datetime

@dataclass
class Item:
    name: str
    price: float
    desc: str = self.name

class Ledger:
    def __init__(self, location: Path, overwrite: bool=False) -> Ledger:
        self.location = location
        self.location.touch(exist_ok=True)

    def make_transaction(self, payer: str, amount: float|int, payee: str)->None:
        with open(self.location, 'a') as ledger:
            ledger.write(f'{payer.lower()}:{amount}:{payee.lower()}')
            
    def purchase(self, payer: str, amount: float|int)->None:
        self.make_transaction(payer, amount, payee="EXT")

    def get_payments_from(self, payer: str)->list:
        transactions_to_people = []
        external_transactions = []

        ledger = open(self.location, 'r')
        for line in ledger.readlines():
            l = line.split(':')
            if l[0] == payer.lower() and l[2] == "EXT":
                pass
            elif l[0] == payer.lower():
                transactions_to_people.append(line)
        ledger.close()

        return transactions_to_people, external_transactions

    # TODO UPDATE THIS 
    def get_total_amount_from(self, payer:str)->list:
        return sum([x.split(':')[1] for x in self.get_payments_from(payer)])
