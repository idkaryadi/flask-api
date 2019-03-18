import logging, json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from blueprints.auth import *
from blueprints.client import *
from blueprints.user import *
from flask_jwt_extended import jwt_required, get_jwt_claims

from . import *

bp_admin = Blueprint('admin', __name__)
api = Api(bp_admin)

class AdminUserResource(Resource):

    @jwt_required
    def get(self, id = None):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'admin':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}
        if id is None:
            rows = []
            output = dict()
            for row in Users.query.all():
                rows.append(marshal(row, Users.respond_field))
            output["All User"] = rows
            return output, 200, {'Content-Text':'application/json'}
        else:
            qry = Users.query.get(id)
            if qry is None:
                return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}
            return marshal(qry, Users.respond_field), 200, {'Content-Text':'application/json'}

    @jwt_required
    def post(self):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'admin':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        parser = reqparse.RequestParser()
        parser.add_argument('username', location = 'json')
        parser.add_argument('password', location = 'json')
        args = parser.parse_args()

        user = Users(None, args['username'], args['password'], "user")
        db.session.add(user)
        db.session.commit()
        
        return {"status": "Success Added User Data"}, 200, {'Content-Text':'application/json'}

    @jwt_required
    def put(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'admin':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        parser = reqparse.RequestParser()
        parser.add_argument('username', location = 'json')
        parser.add_argument('password', location = 'json')
        args = parser.parse_args()

        qry = Users.query.get(id)
        if qry is None:
            return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}
        
        if args['username'] is not None:
            qry.username = args['username']
        if args['password'] is not None:
            qry.password = args["password"]
        
        db.session.commit()
        return {"status": "Success Updated User Data"}, 200, {'Content-Text':'application/json'}
    
    @jwt_required
    def delete(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'admin':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}
        
        qry = Users.query.get(id)
        
        if qry is None:
            return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}

        db.session.delete(qry)
        db.session.commit()
        return {"status": "Success deleted"}, 200, {'Content-Text':'application/json'}

api.add_resource(AdminUserResource, '/admin/user', '/admin/user/<int:id>')

class AdminClientResource(Resource):

    @jwt_required
    def get(self, id = None):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'admin':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}
        if id is None:
            rows = []
            output = dict()
            for row in Clients.query.all():
                rows.append(marshal(row, Clients.respond_field))
            output["All Clients"] = rows
            return output, 200, {'Content-Text':'application/json'}
        else:
            qry = Clients.query.get(id)
            if qry is None:
                return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}
            return marshal(qry, Clients.respond_field), 200, {'Content-Text':'application/json'}

    @jwt_required
    def post(self):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'admin':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        parser = reqparse.RequestParser()
        parser.add_argument('username', location = 'json')
        parser.add_argument('password', location = 'json')
        args = parser.parse_args()

        client = Clients(None, args['username'], args['password'], "client")
        db.session.add(client)
        db.session.commit()
        
        return {"status": "Success Added Client Data"}, 200, {'Content-Text':'application/json'}

    @jwt_required
    def put(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'admin':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        parser = reqparse.RequestParser()
        parser.add_argument('username', location = 'json')
        parser.add_argument('password', location = 'json')
        args = parser.parse_args()

        qry = Clients.query.get(id)
        if qry is None:
            return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}
        
        if args['username'] is not None:
            qry.username = args['username']
        if args['password'] is not None:
            qry.password = args["password"]
        
        db.session.commit()
        return {"status": "Success Updated User Data"}, 200, {'Content-Text':'application/json'}
    
    @jwt_required
    def delete(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'admin':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}
        
        qry = Clients.query.get(id)
        
        if qry is None:
            return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}

        db.session.delete(qry)
        db.session.commit()
        return {"status": "Success deleted"}, 200, {'Content-Text':'application/json'}

api.add_resource(AdminClientResource, '/admin/client', '/admin/client/<int:id>')

class AdminProductsResource(Resource):

    @jwt_required
    def get(self, id = None):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'admin':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}
        
        # client_id = jwtClaims['id']
        # Product = Products.query.filter_by(client_id = client_id)

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
            output["total_page"] = 6 # round(Barangs.count()/args['rp'])
            output["per_page"] = args['rp']
            output["hasil"] = rows
            
            return output, 200, {'Content-Text':'application/json'}
        else:
            qry = Products.query.get(id)
            # if  qry.client_id != client_id:
            #     return {"status": "Not Your Product"}, 404, {'Content-Text':'application/json'}

            if qry is not None:
                output["page"] = args['p']
                output["total_page"] = 6 # round(len(Ta)/args['rp'])
                output["per_page"] = args['rp']
                output["hasil"] = marshal(qry, Products.respond_field)
                return output, 200, {'Content-Text':'application/json'} 
        return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}

    @jwt_required
    def post(self):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'admin':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        parser = reqparse.RequestParser()
        parser.add_argument('nama', location = 'json')
        parser.add_argument('vendor', location = 'json')
        parser.add_argument('deskripsi', location = 'json')
        parser.add_argument('product_type_id', location = 'json')
        parser.add_argument('price', location = 'json')
        parser.add_argument('status', location = 'json')
        parser.add_argument('url_picture', location = 'json')
        parser.add_argument('qty', location = 'json')
        parser.add_argument('client_id', location = 'json')
        args = parser.parse_args()

        qry = Clients.query.get(args['client_id'])
        if qry is None:
            return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}

        product = Products(
            None, args['nama'], args['vendor'], args['deskripsi'], args['product_type_id'], args['price'],
            args['status'], args['url_picture'], args['qty'], args['client_id'])
        db.session.add(product)
        db.session.commit()

        return {"status": "Add Success"}, 200, {'Content-Text':'application/json'}

    @jwt_required
    def put(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'admin':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        parser = reqparse.RequestParser()
        parser.add_argument('nama', location = 'json')
        parser.add_argument('vendor', location = 'json')
        parser.add_argument('deskripsi', location = 'json')
        parser.add_argument('product_type_id', location = 'json')
        parser.add_argument('price', location = 'json')
        parser.add_argument('status', location = 'json')
        parser.add_argument('url_picture', location = 'json')
        parser.add_argument('qty', location = 'json')
        parser.add_argument('client_id', location = 'json')
        args = parser.parse_args()

        qry = Clients.query.get(args['client_id'])
        if qry is None:
            return {"status": "CLIENT ID NOT EXIST"}, 404, {'Content-Text':'application/json'}

        qry = Products.query.get(id)
        if qry is None:
            return {"status": "NOT_FOUND"}, 404, {'Content-Text':'application/json'}
        
        # qry.deskripsi = args['deskripsi']
        if args['nama'] is not None:
            qry.nama = args['nama']
        if args['vendor'] is not None:
            qry.vendor = args['vendor']
        if args['deskripsi'] is not None:
            qry.deskripsi = args['deskripsi']
        if args['product_type_id'] is not None:
            qry.product_type_id = args['product_type_id']
        if args['price'] is not None:
            qry.price = args['price']
        if args['status'] is not None:
            qry.status = args['status']
        if args['url_picture'] is not None:
            qry.url_picture = args['url_picture']
        if args['qty'] is not None:
            qry.qty = args['qty']
        if args['client_id'] is not None:
            qry.client_id = args['client_id']

        db.session.commit()
        return {"status": "Success Updated"}, 200, {'Content-Text':'application/json'}    
    
    @jwt_required
    def delete(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims["status"] != "admin":
            return {"status": "NOT_FOUND"}, 404, {'Content-Text':'application/json'}
        
        qry = Products.query.get(id)
        if qry is None:
            return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}
        db.session.delete(qry)
        db.session.commit()
        return {"status": "Success deleted"}, 200, {'Content-Text':'application/json'}

api.add_resource(AdminProductsResource, '/admin/product', '/admin/product/<int:id>')

# Untuk pengembangan
"""
class AdminTransactionDetailsResource(Resource):

    @jwt_required
    def get(self, id = None):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'admin':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        if id is None:
            parser = reqparse.RequestParser()
            parser.add_argument('p', type=int, location = 'args', default = 1)
            parser.add_argument('rp', type=int, location = 'args', default = 5)

            args = parser.parse_args()

            offset = (args['p'] * args['rp']) - args['rp']
            
            output = dict()
            qry = Transaction_Details.query
                
            rows = []
            for row in qry.limit(args['rp']).offset(offset).all():
                rows.append(marshal(row, Transaction_Details.respond_field))
            
            output["page"] = args['p']
            output["total_page"] = 6 # round(Transaction_Details.count()/args['rp'])
            output["per_page"] = args['rp']
            output["hasil"] = rows
            
            return output, 200, {'Content-Text':'application/json'}
        else:
            qry = Transaction_Details.query.get(id)
            output = dict()
            if qry is not None:
                # output["page"] = args['p']
                # output["total_page"] = 6 # round(len(Ta)/args['rp'])
                # output["per_page"] = args['rp']
                # output["hasil"] = marshal(qry, Transaction_Details.respond_field)
                # return output, 200, {'Content-Text':'application/json'}
                return marshal(qry, Transaction_Details.respond_field), 200, {'Content-Text':'application/json'} 
        return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}

api.add_resource(AdminTransactionDetailsResource, '/admin/transaction_detail', '/admin/transaction_detail/<int:id>')

class AdminTransactionsResource(Resource):

    @jwt_required
    def get(self, id = None):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'admin':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        if id is None:
            parser = reqparse.RequestParser()
            parser.add_argument('p', type=int, location = 'args', default = 1)
            parser.add_argument('rp', type=int, location = 'args', default = 5)

            args = parser.parse_args()

            offset = (args['p'] * args['rp']) - args['rp']
            
            output = dict()
            qry = Transactions.query
                
            rows = []
            for row in qry.limit(args['rp']).offset(offset).all():
                rows.append(marshal(row, Transactions.respond_field))
            
            output["page"] = args['p']
            output["total_page"] = 6 # round(Transactions.count()/args['rp'])
            output["per_page"] = args['rp']
            output["hasil"] = rows
            
            return output, 200, {'Content-Text':'application/json'}
        else:
            qry = Transactions.query.get(id)
            output = dict()
            if qry is not None:
                output["page"] = args['p']
                output["total_page"] = 6 # round(len(Ta)/args['rp'])
                output["per_page"] = args['rp']
                output["hasil"] = marshal(qry, Transactions.respond_field)
                return output, 200, {'Content-Text':'application/json'} 
        return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}

api.add_resource(AdminTransactionsResource, '/admin/transaction', '/admin/transaction/<int:id>')
"""

class AdminTransactionsResource(Resource):

    @jwt_required
    def get(self, id = None):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'admin':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        if id is None:
            parser = reqparse.RequestParser()
            parser.add_argument('p', type=int, location = 'args', default = 1)
            parser.add_argument('rp', type=int, location = 'args', default = 5)

            args = parser.parse_args()

            offset = (args['p'] * args['rp']) - args['rp']
            
            output = dict()
            qry = Transactions.query
                
            rows = []
            for row in qry.limit(args['rp']).offset(offset).all():
                rows.append(marshal(row, Transactions.respond_field))
            
            output["page"] = args['p']
            output["total_page"] = 6 # round(Transactions.count()/args['rp'])
            output["per_page"] = args['rp']
            output["hasil"] = rows
            
            return output, 200, {'Content-Text':'application/json'}
        else:
            qry = Transactions.query.get(id)
            output = dict()
            if qry is not None:
                output["page"] = args['p']
                output["total_page"] = 6 # round(len(Ta)/args['rp'])
                output["per_page"] = args['rp']
                output["hasil"] = marshal(qry, Transactions.respond_field)
                return output, 200, {'Content-Text':'application/json'} 
        return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}

api.add_resource(AdminTransactionsResource, '/admin/transaction', '/admin/transaction/<int:id>')