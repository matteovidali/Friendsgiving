from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
from person import Person, get_name_or_id, ids
from random import randint
from PIL import Image
import json

ids = ids
people = {}

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

def create_filesystem(path):
    path.mkdir(parents=True)

def create_pigeon_data(path, fname):
    if not path.exists():
        create_filesystem(path)

    if (path / fname).is_file():
        return

    pigeon_data = {'num_pigeons': 0,
                   'pigeon_pictures': {0: f'{path}/assets/null_pigeon.gif'},
                   'pigeon_desc': {0: 'n̸̍̍͊͑͊̀̓̍̽͛͘͜ų̸̞̲̟̪̲͖͇͈̰̬̋̀̽̈́̍͊̍̍͂l̶̟̼̺̬̖̝̹̦̫̹͖͙̐̂͛͊̈͘̚͜͝l̸̢̠̣̳͎̻̝̗̹͚̇͆̉̽͐̀̉̅͠͠ ̷͉͉̞̥̥̖̍̑ͅp̴̛̖̲͇̜̹͈̤̖̽͐̍̍̐̄̓̇̃̂̾̍͒̚i̵̢̧̨̧̺̮̻͇͆̈́̔̔̀g̴̢͎̮͓̫̯̺͎̣̳͖͛̌͘é̴̛̛̄͊̍̍͌̐͂̎͜õ̵̡̢̙̖̯̪̯̪̀͊͛̒̓̈̀̐́̑̒̈́̌̕͠n̷̥̘̬̳̖̙̳̺̈̓̀̂̐̚͜͝͠'}}

    with open(path / fname, 'w+') as jsonfile:
        json.dump(pigeon_data, jsonfile)

    return pigeon_data

def resize_image(image_path, size=(300,300)):
    with Image.open(image_path) as img:
        img.thumbnail(size)
        img.save(image_path)

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


app.before_request_funcs = [(None, create_people()), (None, create_pigeon_data(Path('./static/pigeons'), 'pigeon_metadata.json'))]

def get_name_from_id(id):
    global ids
    print(id, type(id))
    return get_name_or_id(id, ids)

def get_id_from_name(name):
    global ids
    return get_name_or_id(name, ids)

@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/<id>/home/', methods=['GET', 'POST'])
def custom(id):
    user_id = id
    global people
    if user_id not in people.keys() and user_id != 'pigeon':
        return f"That is not an appropriate secret key."
    return render_template('home.html', name=get_name_from_id(user_id), id=user_id)

@app.route('/validate/', methods=['GET', 'POST'])
def go_home():
    return redirect(url_for("custom", id=request.form['user_id']))

@app.route('/<id>/home/expense_splitter/')
def expense_form(id):
    global people
    return render_template('payment_form.html', people=people.values(), buyer=get_name_from_id(id))

@app.route('/<id>/home/what_do_i_owe/')
def what_do_i_owe(id):
    global people,ids
    return render_template('what_do_i_owe.html', person=people[id], secret=id, ids=ids)

@app.route('/<id>/home/what_the_fuck_did_i_buy/')
def what_the_fuck_did_i_buy(id):
    global people,ids
    stuff = people[id].get_purchases()
    return render_template('what_the_fuck_did_i_buy.html', person=people[id], stuff=stuff)

def pigeon_file_update(path: str, fname:str, image_path: str, desc: str):
    with open(path / fname) as pigeon_file:
        p_metadata = json.load(pigeon_file)

    p_metadata['num_pigeons'] = int(p_metadata['num_pigeons'])+1
    np = p_metadata['num_pigeons']
    print("ADDING PIGEON"+str(np))
    p_metadata['pigeon_pictures'][np] = image_path
    p_metadata['pigeon_desc'][np] = desc

    print(p_metadata)
    with open(path / fname, 'w+') as pfile:
        json.dump(p_metadata, pfile)
    #TODO: Update this
    return p_metadata

@app.route('/pigeon')
def pigeon():
    p_path = Path('static/pigeons')
    r_path = Path('.') / p_path
    #if not r_path.is_file():
    #   create_pigeon_data(p_path, 'pigeon_metadata.json')

    with open(p_path / 'pigeon_metadata.json') as jsonfile:
        p_meta = json.load(jsonfile)

    print(p_meta)
    num_pigeons = p_meta['num_pigeons']
    print(num_pigeons)
    rand_pigeon = randint(0, num_pigeons)
    pigeon_image = p_meta['pigeon_pictures'][f'{rand_pigeon}']
    print(pigeon_image)
    pigeon_desc = p_meta['pigeon_desc'][f'{rand_pigeon}']
    return render_template('pigeon.html', pigeon_img=pigeon_image, pigeon_desc=pigeon_desc)

@app.route('/i_wanna_submit/submit_a_pigeon', methods=['GET', 'POST'])
def submit_a_pigeon():
    if request.method == 'POST':
        with open('./static/pigeons/pigeon_metadata.json') as json_file:
            p_data = json.load(json_file)

        np = int(p_data['num_pigeons'])
        pigeon_image = request.files['pigeon_image']
        pigeon_desc = request.form['pigeon_desc']
        # Save the uploaded image to the 'uploads' folder (create the folder if not exists)
        pigeon_image.save(f'static/pigeons/assets/{np+1}.jpg')
        resize_image(f'static/pigeons/assets/{np+1}.jpg')
        pigeon_file_update(Path('static/pigeons'),
                           'pigeon_metadata.json',
                           f'static/pigeons/assets/{np+1}.jpg', 
                           pigeon_desc)
        #result_message = f"Image '{pigeon_image.filename}' uploaded successfully with description: {pigeon_desc}"
        return 'wtf man...'
    return render_template('submit_a_pigeon.html')

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

