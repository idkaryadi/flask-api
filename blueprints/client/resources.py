import logging, json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from blueprints.auth import Users
from blueprints.client import Products, Product_Types
# from blueprints.user import Transaction_Details
from flask_jwt_extended import jwt_required, get_jwt_claims
from werkzeug.security import generate_password_hash, \
    check_password_hash
import math as ma
from flask_cors import CORS
from . import *

bp_client = Blueprint('client', __name__)
CORS(bp_client)
api = Api(bp_client)

# Bagian Resource untuk Users
# class ClientResource(Resource):

#     @jwt_required
#     def get(self):
#         jwtClaims = get_jwt_claims()
#         if jwtClaims['status'] != 'client':
#             return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}
#         client_id = jwtClaims['id']
#         qry = Users.query.get(client_id)
#         if qry is None:
#             return {"message": "Your Account is deleted by your self"}, 404, {'Content-Text':'application/json'}
#         # return jwtClaims, 200, {'Content-Text':'application/json'}
#         return {"status": "oke", "data": marshal(qry, Users.respond_field)}, 200, {'Content-Text':'application/json'}

#     @jwt_required
#     def put(self):
#         jwtClaims = get_jwt_claims()

#         if jwtClaims['status'] != 'client':
#             return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

#         parser = reqparse.RequestParser()
#         parser.add_argument('username', location = 'json')
#         parser.add_argument('password', location = 'json')
#         parser.add_argument('email', location = 'json')
#         parser.add_argument('lokasi', location = 'json')
#         args = parser.parse_args()

#         client_id = jwtClaims["id"]
#         qry = Users.query.get(client_id)
#         if qry is None:
#             return {"status": "Your Account is deleted by your self"}, 404, {'Content-Text':'application/json'}

#         if args['username'] is not None:
#             qry.username = args['username']
#         if args['lokasi'] is not None:
#             qry.lokasi = args['lokasi']
#         if args['email'] is not None:
#             qry.email = args['email']
#         if args['password'] is not None:
#             qry.password = generate_password_hash(args["password"])
        
#         db.session.commit()
#         return {"status": "oke", "data": marshal(qry, Users.respond_field)}, 200, {'Content-Text':'application/json'}
    
#     @jwt_required
#     def delete(self):
#         jwtClaims = get_jwt_claims()
#         if jwtClaims['status'] != 'client':
#             return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}
        
#         client_id = jwtClaims["id"]
#         qry = Users.query.get(client_id)

#         if qry is None:
#             return {"status": "Your Account is deleted by your self"}, 404, {'Content-Text':'application/json'}

#         db.session.delete(qry)
#         db.session.commit()
#         return {"status": "oke", "data": marshal(qry, Users.respond_field)}, 200, {'Content-Text':'application/json'}

# api.add_resource(ClientResource, '/client')

class ClientProductsResource(Resource):

    @jwt_required
    def get(self, id = None):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'client':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}
        
        client_id = jwtClaims['id']
        Product = Products.query.filter_by(client_id = client_id)

        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location = 'args', default = 1)
        parser.add_argument('rp', type=int, location = 'args', default = 20)
        parser.add_argument('q', location = 'args', default = "")

        args = parser.parse_args()

        offset = (args['p'] * args['rp']) - args['rp']
    
        output = dict()

        if id is None:
            qry = Product
            if args['q'] is not "":
                qry = qry.filter_by(nama=args['q'])
                output["pencarian"] = args['q']
                
            rows = []
            total_page = 0
            for row in qry.limit(args['rp']).offset(offset).all():
                # get kategori name
                product_type_id = row.product_type_id
                pt_qry = Product_Types.query.get(product_type_id)
                if pt_qry is None:
                    kategori_produk = "Unknown"
                else:
                    kategori_produk = pt_qry.nama
                tambahan = dict()
                tambahan["kategori_produk"] = kategori_produk

                # add kategori name
                rows.append({"ori":marshal(row, Products.respond_field), "tambahan":tambahan})
                total_page = total_page +1

            output['status'] = 'oke'
            output["page"] = args['p']
            output["total_page"] = ma.ceil(total_page/args['rp'])
            output["per_page"] = args['rp']
            output["data"] = rows
            
            return output, 200, {'Content-Text':'application/json'}
        else:
            qry = Products.query.get(id)
            if  qry.client_id != client_id:
                return {"status": "Not Your Product"}, 404, {'Content-Text':'application/json'}

            if qry is not None:
                output['status'] = 'oke'
                output["data"] = marshal(qry, Products.respond_field)
                return output, 200, {'Content-Text':'application/json'} 
        return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}

    @jwt_required
    def post(self):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'client':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        client_id = jwtClaims['id']
        lokasi = jwtClaims['lokasi']
        parser = reqparse.RequestParser()
        parser.add_argument('nama', location = 'json', required = True)
        parser.add_argument('deskripsi', location = 'json')
        parser.add_argument('product_type_id', location = 'json', required = True)
        parser.add_argument('price', location = 'json', required = True)
        parser.add_argument('satuan', location = 'json', required = True)
        parser.add_argument('status', location = 'json', required = True)
        parser.add_argument('url_picture', location = 'json')
        parser.add_argument('qty', location = 'json', required = True)

        args = parser.parse_args()

        product = Products(
            None, args['nama'], args['deskripsi'], args['product_type_id'], args['price'],
            args['satuan'], args['status'], args['url_picture'], args['qty'], client_id, lokasi, 0)
        db.session.add(product)
        db.session.commit()
        qry = Products.query.filter_by(client_id=client_id).order_by(Products.id.desc()).first()

        return {"status": "oke", "data":marshal(qry, Products.respond_field)}, 200, {'Content-Text':'application/json'}

    @jwt_required
    def put(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'client':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        parser = reqparse.RequestParser()
        parser.add_argument('nama', location = 'json')
        parser.add_argument('deskripsi', location = 'json')
        parser.add_argument('product_type_id', location = 'json')
        parser.add_argument('price', location = 'json')
        parser.add_argument('satuan', location = 'json')
        parser.add_argument('status', location = 'json')
        parser.add_argument('url_picture', location = 'json')
        parser.add_argument('qty', location = 'json')
        args = parser.parse_args()

        qry = Products.query.get(id)
        if qry is None:
            return {"status": "NOT_FOUND"}, 404, {'Content-Text':'application/json'}
        
        # qry.deskripsi = args['deskripsi']
        if args['nama'] is not None:
            qry.nama = args['nama']
        if args['deskripsi'] is not None:
            qry.deskripsi = args['deskripsi']
        if args['product_type_id'] is not None:
            qry.product_type_id = args['product_type_id']
        if args['price'] is not None:
            qry.price = args['price']
        if args['satuan'] is not None:
            qry.satuan = args['satuan']
        if args['status'] is not None:
            qry.status = args['status']
        if args['url_picture'] is not None:
            qry.url_picture = args['url_picture']
        if args['qty'] is not None:
            qry.qty = args['qty']
        
        db.session.commit()
        return {"status": "oke", "data":marshal(qry, Products.respond_field)}, 200, {'Content-Text':'application/json'}    
    
    @jwt_required
    def delete(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims["status"] != "client":
            return {"status": "Invalid Status"}, 404
        
        qry = Products.query.get(id)
        if qry is None:
            return {"status": "DATA_NOT_FOUND"}, 404
        db.session.delete(qry)
        db.session.commit()
        return {"status": "oke", "data":marshal(qry, Products.respond_field)}, 200

api.add_resource(ClientProductsResource, '/client/product', '/client/product/<int:id>')

# Buat pengembangan
"""
# Buat pengembangan
# Belum jalan
class ClientTransactionDetailsResource(Resource):
    
    @jwt_required
    def get(self, id = None):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'client':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}
        
        client_id = jwtClaims['id']

        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location = 'args', default = 1)
        parser.add_argument('rp', type=int, location = 'args', default = 5)
        parser.add_argument('q', location = 'args', default = "")

        args = parser.parse_args()

        offset = (args['p'] * args['rp']) - args['rp']
        
        output = dict()
        product = Products.query.filter_by(client_id = client_id)
        # Problem
        qry = Transaction_Details.query.where(product_id in product.id)
        if args['q'] is not "":
            qry = qry.filter_by(nama=args['q'])
            output["pencarian"] = args['q']
            
        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Transaction_Details.respond_field))
        
        output["page"] = args['p']
        output["total_page"] = 6 # Products.query().count()/args['rp'])
        output["per_page"] = args['rp']
        output["hasil"] = rows
        
        return output, 200, {'Content-Text':'application/json'}

api.add_resource(ClientTransactionDetailsResource, '/client/transaction_detail')
"""

class ClientTransactionResource(Resource):
    @jwt_required
    def get(self, product_id):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'client':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        client_id = jwtClaims['id']
        
        # if id is None:
        #     parser = reqparse.RequestParser()
        #     parser.add_argument('p', type=int, location = 'args', default = 1)
        #     parser.add_argument('rp', type=int, location = 'args', default = 5)

        #     args = parser.parse_args()

        #     offset = (args['p'] * args['rp']) - args['rp']
            
        #     output = dict()
        #     qry = Transactions.query.filter_by(user_id = user_id)
                
        #     rows = []
        #     for row in qry.limit(args['rp']).offset(offset).all():
        #         rows.append(marshal(row, Transactions.respond_field))
            
        #     output["page"] = args['p']
        #     output["total_page"] = 6 # round(Transactions.count()/args['rp'])
        #     output["per_page"] = args['rp']
        #     output["hasil"] = rows
            
        #     return output, 200, {'Content-Text':'application/json'}
        # else:

        product = Products.query.get(product_id)
        if product is None:
            return {"status": "DATA_NOT_FOUND, this id not in your product"}, 404, {'Content-Text':'application/json'}
        qry = Transactions.query.filter_by(product_id = product_id)

        if qry is not None:
            rows = []
            for row in qry.all():
                rows.append(marshal(row, Transactions.respond_field))
                
            return rows, 200, {'Content-Text':'application/json'} 
        return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}

api.add_resource(ClientTransactionResource, '/client/transaction/<int:id>')