from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config['SECRET_KEY'] = '83f245c53e00618f02731bae1ae112a4'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///application.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from api import routes
