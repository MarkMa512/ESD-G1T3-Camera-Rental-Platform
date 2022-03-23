# python -m pip install "pymongo[srv]"


from flask import Flask, request, url_for
from flask_pymongo import PyMongo


app = Flask(__name__)
# app.config["MONGO_URL"] = 'mongodb+srv: // dbESDImage: < password > @cluster0.g2j6s.mongodb.net/ESDImages?retryWrites = true & w = majority'
# delete b4 push!
mongo = PyMongo(app)


@app.route('/upload_image')
def uploadImage():
    return '''
        <form method="POST" action="/create" enctype="multipart/form-data">
            <input type = "text" name="username">
            <input type = "file" name="profile_image"> 
            <input type = submit>
        </form>
    '''


@app.route('/create', methods=['POST'])
def create():
    if 'profile_image' in request.files:
        profile_image = request.files['profile_image']
        mongo.save_file(profile_image.filename, profile_image)
        mongo.db.users.insert_one({'username': request.form.get(
            'username'), 'profile_image_name': profile_image.filename})
    return "Success!"


@app.route('/show_image')
def show_image():
    return mongo.send_file('Test1.jpg')


@app.route('/profile/<path:username>')
def profile(username):
    user = mongo.db.users.find_one_or_404({'username': username})
    return f'''
        <h1> {username}</h1>
        <img src="{url_for('show_image', filename = user['profile_image_name'])}">
    '''


app.run(debug=True)
