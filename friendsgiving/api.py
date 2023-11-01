from flask import Flask, render_template, request
from pathlib import Path
from person import Person, get_name_or_id, ids

ids = ids
people = {}

app = Flask(__name__)

def create_people():
    global people, ids
    
    for id, name in ids.items():
        p = Path(f"./id_file/{name.lower()}_id")
        if p.is_file():
            person = Person(name, id=id)
        else:
            person = Person(name, id=id, 
                            owes={g: 0 for g in ids.keys() if g != id}, 
                            what_for={g: [] for g in ids.keys() if g != id})
        people[person.id] = person


app.before_request_funcs = [(None, create_people())]

def get_name_from_id(id):
    global ids
    print(id, type(id))
    return get_name_or_id(id, ids)

def get_id_from_name(name):
    global ids
    return get_name_or_id(name, ids)

@app.route('/')
def home():
    return "You must go to this url as follows: <url>/secret_id"

@app.route('/<id>/')
def custom(id):
    global people
    if id not in people.keys():
        return f"That is not an appropriate secret key {people.keys()}"
    return render_template('home.html', name=get_name_from_id(id), id=id)

@app.route('/<id>/expense_splitter/')
def expense_form(id):
    global people
    return render_template('payment_form.html', people=people.values(), buyer=get_name_from_id(id))

@app.route('/<id>/what_do_i_owe/')
def what_do_i_owe(id):
    global people,ids
    return render_template('what_do_i_owe.html', person=people[id], secret=id, ids=ids)

@app.route('/<id>/what_the_fuck_did_i_buy/')
def what_the_fuck_did_i_buy(id):
    global people,ids
    stuff = people[id].get_purchases()
    return render_template('what_the_fuck_did_i_buy.html', person=people[id], stuff=stuff)

@app.route('/process/', methods=['POST'])
def process_form():
    item = request.form['item']
    buyer_id = get_id_from_name(request.form['buyer'].lower())
    amount = request.form['amount']
    split_with = [key for key in request.form if key != 'item' and key != 'amount' and key != 'buyer']

    people[buyer_id].buys(item, amount)
    split = 0
    for n in split_with:
        n = get_id_from_name(n)
        if n == buyer_id:
            continue
        people[n].owes[buyer_id] += round(float(amount) / len(split_with), 2)
        split = round(float(amount) / len(split_with), 2)
        people[n].what_for[buyer_id].append(item)
        people[n].update()

    #return f"Sucessfully purchased {item} for ${amount}. {', '.join(split_with)} will each be charged ${split}"
    return render_template('thanks_for_payment.html', name=get_name_from_id(buyer_id), id=buyer_id)

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

