from safrafinaceira import db, app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, LargeBinary
import uuid

class User(db.Model):
    __tablename__ = 'User'
    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    status = db.Column(db.String)
    token_mfa = db.Column(db.String)

    def __repr__(self):
        return f"User('{self.uid}','{self.username}','{self.password}','{self.status}','{self.token_mfa}')"

    def get_id(self):
        return (self.uid)

    def to_json(self):
        return {'uid':self.uid,'username': self.username, 'password': self.password, 'status': self.status, 'token_mfa': self.token_mfa}

class IDs(db.Model):
    __tablename__ = 'IDs'
    guid = db.Column(db.String, primary_key=True)
    expired_at = db.Column(db.DateTime)

    def __repr__(self):
        return f"IDs('{self.guid}','{self.expired_at}')"

    def get_id(self):
        return (self.guid)

    def to_json(self):
        return {'guid':self.guid,'username': self.expired_at_at}


with app.app_context():
    db.drop_all()
    db.create_all()

   
    users = []
    ids = []

    for _ in range(100):
        ids.append(IDs(guid=str(uuid.uuid4())))
    #users.append(User(username='rodrigo.silva@safra.com.br', password="gAAAAABoki-FIGCHP_cpqKXNaF82RoXd8_9YViMkPHaxtP5nbQjbc2vUcOQL-qNR0h94EKulNNygFvv-q3gEAWfNy0ek_0kNwQ==", status="NEW_USER", token_mfa="123"))
    
    ids.append(IDs(guid="3f886ea1-fb90-4583-813a-635c34aacd24"))

    for Id in ids:
        db.session.add(Id)

    for user in users:
        db.session.add(user)
    
    

    db.session.commit()