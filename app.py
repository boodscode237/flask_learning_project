from flask import Flask, jsonify, request, url_for, redirect, session, render_template, g
import random
import sqlite3

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret_key'

def connect_db():
    """To connect to the data base"""
    sql = sqlite3.connect('data.db')
    ''' To display the database like a row instead of tuple'''
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite3'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def hello_world():
    session.pop('name', None)
    return f'<h1>Hello World!</h1>'

@app.route('/home', methods=['POST', 'GET'], defaults={'name': 'Unknown'})
@app.route('/home/<string:name>', methods=['POST', 'GET'])
def home(name):
    session['name'] = name
    db = get_db()
    cur = db.execute('select id, name, location from users')
    results = cur.fetchall()

    return render_template('home.html', name=name, display=True, my_list=['one', 'Two', 'Three', 4],
                           list_of_dictionaries=[{'name': 'John'}, {'name': 'Doe'}], results=results)

@app.route('/json')
def json():
    if 'name' in session:
        name = session['name']
    else:
        name = 'Nothing in the session'
    return jsonify({'key': 'value', 'key_list': [1, 2, 3, 4], 'name': name})

@app.route('/query')
def query():
    name = request.args.get('name')
    location = request.args.get('location')
    return f'<h1>Hi {name} from {location}. You are on the same page!</h1>'

@app.route('/theform', methods=["GET", "POST"])
def the_form():
    if request.method == 'GET':
        return render_template('form.html')
    else:
        name = request.form["name"]
        location = request.form["location"]

        db = get_db()
        db.execute('insert into users (name, location) values(?, ?)', [name, location])
        db.commit()

        return redirect(url_for('home', name=name, location=location))
        # return f'<h1>Hello {name} You are from {location}?</h1>'


'''
@app.route('/process', methods=['POST'])
def process():
    name = request.form["name"]
    location = request.form["location"]
    return f'<h1>Hello {name} You are from {location}?</h1>'
'''

@app.route('/processjson', methods=['POST'])
def process_json():
    data = request.get_json()
    name = data['name']
    location = data['location']
    randomlist = data['randomlist']
    return jsonify({'result': 'success', 'name': name, "location": location,
                    'random_key_in_list': randomlist[random.randint(0, 3)]})

@app.route('/viewresults')
def view_results():
    db = get_db()
    cur = db.execute("select id, name,location from users")
    results = cur.fetchall()
    return '<h1>The id is {}. The name is {}. The location is {}.</h1>'.format(results[1]['id'], results[1]['name'],
                                                                               results[1]['location'])


if __name__ == '__main__':
    app.run()
