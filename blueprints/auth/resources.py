import logging, json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
from blueprints.auth import *
from werkzeug.security import generate_password_hash, \
    check_password_hash

bp_auth = Blueprint('auth', __name__)
api = Api(bp_auth)

class CreateTokenResources(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', location='args', required=True)
        parser.add_argument('password', location='args', required=True)
        args = parser.parse_args()
        
        qry = Users.query.filter_by(username=args['username']).first()
        if qry != None :
            validasi = check_password_hash(qry.password, args['password'])
            if not validasi:
                return {'status':'UNAUTHORIZED', 'message':'invalid password'}, 401 
            token = create_access_token(marshal(qry, Users.respond_field))
        else : 
            return {'status':'UNAUTHORIZED', 'message':'invalid username'}, 401
        return {"status":"oke", 'token': token}, 200

api.add_resource(CreateTokenResources, '/token')