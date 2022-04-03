from flask import Flask, request, Response, jsonify
from werkzeug.utils import secure_filename
from flask import redirect

from db import db_init, db
from models import Img
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///img.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)
CORS(app)


@app.route('/')
def hello_world():
    return 'Image Microservice running!'


@app.route('/upload', methods=['POST'])
def upload():
    pic = request.files['pic']
    if not pic:
        return 'No pic uploaded!', 400

    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    if not filename or not mimetype:
        return 'Bad upload!', 400

    img = Img(img=pic.read(), name=filename, mimetype=mimetype)
    db.session.add(img)
    db.session.commit()

    return jsonify(
        {
            "code": 200,
            "message": "Image uploaded successfully",
        }
    ), 200


@app.route('/<int:id>')
def get_img(id):
    img = Img.query.filter_by(id=id).first()
    if not img:
        return 'Img Not Found!', 404

    return Response(img.img, mimetype=img.mimetype)


@app.route('/latest')
def get_latest():
    img = Img.query.order_by(Img.id.desc()).first()
    if not img:
        return 'Img Not Found!', 404
    return Response(img.img, mimetype=img.mimetype)


if __name__ == '__main__':
    app.run(host="0.0.0.0" ,host='localhost', port=5302, debug=True)
