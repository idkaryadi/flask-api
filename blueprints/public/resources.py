import logging, json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from blueprints.client import Products
from blueprints.auth import *
import json

from . import *

bp_public = Blueprint('Public', __name__)
api = Api(bp_public)

#Untuk Public
class PublicResource(Resource):

    def get(self, id = None):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location = 'args', default = 1)
        parser.add_argument('rp', type=int, location = 'args', default = 5)
        parser.add_argument('q', location = 'args', default = "")
        args = parser.parse_args()

        offset = (args['p'] * args['rp']) - args['rp']
        output = dict()
        if id is None: 
            qry = Products.query
            if args['q'] is not "":
                qry = qry.filter_by(nama=args['q'])
                output["pencarian"] = args['q']
                
            rows = []
            for row in qry.limit(args['rp']).offset(offset).all():
                rows.append(marshal(row, Products.respond_field))
            
            output["page"] = args['p']
            output["total_page"] = 6 # round(Products.count()/args['rp'])
            output["per_page"] = args['rp']
            output["hasil"] = rows
            
            return output, 200, {'Content-Text':'application/json'}
        else:
            # qry = Products.query.get(id)
            qry = Products.query.filter_by(client_id=id)
            
            rows = []
            for row in qry.limit(args['rp']).offset(offset).all():
                rows.append(marshal(row, Products.respond_field))

            if qry is not None:
                output["page"] = args['p']
                output["total_page"] = 6 # round(len(Products)/args['rp'])
                output["per_page"] = args['rp']
                output["hasil"] = rows # marshal(qry, Products.respond_field)
                return output, 200, {'Content-Text':'application/json'} 
        return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}

    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument('username', location = 'json')
        parser.add_argument('password', location = 'json')
        parser.add_argument('status', location = 'json')

        args = parser.parse_args()

        if args['status'] not in ['user', 'client']: # admin hanya ditambahkan oleh admin
            return {"status": "input status invalid"}, 404, {'Content-Text':'application/json'}
        else:
            new_row = Users(None, args['username'], args['password'], args['status'])
        db.session.add(new_row)
        db.session.commit()

        return {"status": "oke", "data":marshal(new_row, Users.respond_field)}, 200, {'Content-Text':'application/json'}

api.add_resource(PublicResource, '/public', '/public/<int:id>')