from flask import Flask, request
import json, logging
from flask_restful import Resource, Api, reqparse, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_bcrypt import Bcrypt

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@0.0.0.0:3306/WeekendProject'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'SADASsadsadsadsadSADsafaSAdsa0921'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

jwt = JWTManager(app)

@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    return identity

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

#Bcrypt algorithm hashing rounds
BCRYPT_LOG_ROUNDS = 15

api = Api(app, catch_all_404s=True)

@app.after_request
def after_request(response):
    if request.method == 'GET':
        app.logger.warning("REQUEST LOG\t%s %s", request.method, json.dumps({'request': request.args.to_dict(), 'response': json.loads(response.data.decode('utf-8'))}))
    else :
        app.logger.warning("REQUEST LOG\t%s %s", request.method, json.dumps({'request': request.get_json(), 'response': json.loads(response.data.decode('utf-8'))}))
    return response

## call blueprint
from blueprints.public.resources import bp_public
from blueprints.user.resources import bp_user
from blueprints.client.resources import bp_client
# from blueprints.admin.resources import bp_admin
from blueprints.auth.resources import bp_auth

app.register_blueprint(bp_user)
app.register_blueprint(bp_public)
app.register_blueprint(bp_client)
# app.register_blueprint(bp_admin)
app.register_blueprint(bp_auth)

db.create_all()