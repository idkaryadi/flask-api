from blueprints import db
from flask_restful import fields
# from flask_bcrypt import Bcrypt 
from werkzeug.security import generate_password_hash, \
    check_password_hash

class Users(db.Model):

    __tablename__ = "Users"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(10), nullable=False)
    # created_at = db.Column(db.DataTime)
    # updated_at = db.Column(db.DataTime)
    # deleted_at = db.Column(db.DataTime)

    respond_field = {
        'id' : fields.Integer,
        'username' : fields.String,
        # 'password' : fields.String,
        'status' : fields.String
        # 'created_at' : fields.DataTime,
        # 'updated_at' : fields.DataTime,
        # 'deleted_at' : fields.DataTime
    }

    def __init__(self, id, username, password, status): # created_at, updated_at, deleted_at
        self.id = id
        self.username = username
        self.password = generate_password_hash(password)
        self.status = status
        # self.created_at = created_at
        # self.updated_at = updated_at
        # self.deleted_at = deleted_at

    # def check_password(self, password):
    #     return check_password_hash(self.pw_hash, password)

    def __repr__(self):
        return '<Users %r>' % self.id