from flask import Flask
from flask import jsonify
from flask import request
from flask import redirect
from flask import abort
from flask import render_template
from flask_pymongo import PyMongo

import string
import random

# application instance
app = Flask(__name__)

# configuration
app.config['MONGO_DBNAME'] = 'bdnr_db'
app.config['MONGO_URI'] = 'mongodb+srv://uas_bdnr:bdnr2020@bdnr.t8vum.mongodb.net/bdnr_db?retryWrites=true&w=majority'
mongo = PyMongo(app)

# utilities
def avoid_duplicate(url):
    if mongo.db.url_shortener.find_one({'key': url}):
        return False
    else:
        return True

def generate_url():
    chara = string.ascii_letters + string.digits
    url = ''.join((random.choice(chara) for i in range(8)))
    if avoid_duplicate(url):
        return url
    else:
        generate_url()

#rest api
@app.route('/urls', methods=['GET'])
def get_urls():
    url_shortener = mongo.db.url_shortener
    output = []
    for url in url_shortener.find():
        output.append({'key': url['key'], 'original_url': url['original_url']})
    return jsonify(output)

@app.route('/create', methods=['POST'])
def post_url():
    url_shortener = mongo.db.url_shortener

    url = request.json['url']
    key = generate_url()

    create =  url_shortener.insert({'key': key, 'original_url': url})

    created_url = url_shortener.find_one({'key': key})
    return jsonify({
        'key': created_url['key'],
        'original_url': created_url['original_url']
        }), 202
@app.route('/<string:key>', methods=['GET'])
def go_to(key):
    url_shortener = mongo.db.url_shortener

    path = url_shortener.find_one({'key': key})
    if path:
        return redirect(path['original_url'])
    else:
        abort(404)

# web interface
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# main section
if __name__ == '__main__':
    app.run(debug=True)
