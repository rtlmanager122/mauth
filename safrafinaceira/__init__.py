from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# DB Settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///safrafinaceira.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'is4yc{qL2mFr-JnE'

db = SQLAlchemy(app)

from safrafinaceira import routes