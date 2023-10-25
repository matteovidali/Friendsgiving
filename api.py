from flask import Flask, render_template, request
from pathlib import Path
from datetime import datetime, timezone, timedelta
import json

app = Flask(__name__)
tz = timezone(-timedelta(hours=5))
people = {}
ids = {"156156": "Matteo", "252252": "Nia",
       "363363": "Grace", "454454": "Nick", 
       "545545": "Zoe", "656656": "Kye"}

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
        return {'name': self.name, 'i_pay_file': str(self.i_pay_file), 'owes': self.owes, 'what_for': self.what_for, 'total_out':self.total_out}

def get_name_from_id(id):
    global people 
    return people[id].name

def get_id_from_name(name):
    global ids
    for id, n in ids.items():
        if name.lower() == n.lower():
            return id

@app.before_first_request
def create_people():
    global people, ids
    
    for id, name in ids.items():
        p = Path(f"./id_file/{name.lower()}_id")
        if p.is_file():
            person = Person(name, id=id)
        else:
            person = Person(name, id=id, owes={g: 0 for g in ids.keys() if g != id}, what_for={g: [] for g in ids.keys() if g != id})
        people[person.id] = person

@app.route('/')
def home():
    return "You must go to this url as follows: <url>/secret_id"

@app.route('/<id>/')
def custom(id):
    global people
    if id not in people.keys():
        return f"That is not an appropriate secret key {people.keys()}"
    print(id)
    return render_template('home.html', name=get_name_from_id(id), id=id)

@app.route('/<id>/expense_splitter/')
def expense_form(id):
    global people
    return render_template('payment_form.html', people=people.values(), buyer=get_name_from_id(id))

@app.route('/<id>/what_do_i_owe/')
def what_do_i_owe(id):
    global people,ids
    return render_template('what_do_i_owe.html', person=people[id], secret=id, ids=ids)

@app.route('/process/', methods=['POST'])
def process_form():
    print(request.form)
    item = request.form['item']
    buyer_id = get_id_from_name(request.form['buyer'].lower())
    amount = request.form['amount']
    split_with = [key for key in request.form if key != 'item' and key != 'amount' and key != 'buyer']

    print(f"Item: {item}")
    print(f"Amount: ${amount}")
    print(f"Split with: {', '.join(split_with)}")
    people[buyer_id].buys(item, amount)
    
    split = 0
    for n in split_with:
        n = get_id_from_name(n)
        if n == buyer_id:
            continue
        print(people[n].owes)
        people[n].owes[buyer_id] += round(float(amount) / len(split_with), 2)

        split = round(float(amount) / len(split_with), 2)
        people[n].what_for[buyer_id].append(item)
        people[n].update()

    return f"Sucessfully purchased {item} for ${amount}. {', '.join(split_with)} will each be charged ${split}"

@app.route('/<id>/process_payment/', methods=['POST'])
def process_payment(id):
    payment_to = get_id_from_name(request.form['name'])
    all = False
    if 'selectAll' in request.form.keys():
        payment_amount = round(float(people[id].owes[payment_to]), 2)
        all = True
    else:
        p_raw = request.form['amount']
        payment_amount = round(float(p_raw), 2)

    print(payment_to, payment_amount)
    people[id].pays(payment_to, payment_amount, all=all) 
    return render_template('thanks_for_payment.html', name=get_name_from_id(id), id=id)
    
if __name__ == '__main__':
    app.run()

