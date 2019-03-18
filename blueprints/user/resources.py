import logging, json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints.auth import *
from blueprints.client import *
# from blueprints.user import *
from . import *

bp_user = Blueprint('User', __name__)
api = Api(bp_user)

# Bagian Resource untuk Users (#CLEAR)
class UserResource(Resource):

    @jwt_required
    def get(self):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'user':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}
        user_id = jwtClaims['id']
        qry = Users.query.get(user_id)
        if qry is None:
            return {"status": "Your Account is deleted by your self"}, 404, {'Content-Text':'application/json'}
        # return jwtClaims, 200, {'Content-Text':'application/json'}
        return {'status': 'oke', 'data': marshal(qry, Users.respond_field)}, 200, {'Content-Text':'application/json'}

    @jwt_required
    def put(self):
        jwtClaims = get_jwt_claims()

        if jwtClaims['status'] != 'user':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        parser = reqparse.RequestParser()
        parser.add_argument('username', location = 'json')
        parser.add_argument('password', location = 'json')
        args = parser.parse_args()

        user_id = jwtClaims["id"]
        qry = Users.query.get(user_id)
        if qry is None:
            return {"status": "Your Account is deleted by your self"}, 404, {'Content-Text':'application/json'}
        
        if args['username'] is not None:
            qry.username = args['username']
        if args['password'] is not None:
            qry.password = args["password"]
        
        db.session.commit()
        return {"status": "Success Updated User Data", 'data':marshal(qry, Users.respond_field)}, 200, {'Content-Text':'application/json'}
    
    @jwt_required
    def delete(self):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'user':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}
        
        user_id = jwtClaims["id"]
        qry = Users.query.get(user_id)
        
        if qry is None:
            return {"status": "Your Account is deleted by your self"}, 404, {'Content-Text':'application/json'}

        db.session.delete(qry)
        db.session.commit()
        return {"status": "Success deleted", 'data':marshal(qry, Users.respond_field)}, 200, {'Content-Text':'application/json'}

api.add_resource(UserResource, '/user')

class UserTransactionDetailsResource(Resource):

    @jwt_required
    def get(self, id = None):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'user':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        # user_id = jwtClaims['id']
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
            
            output["status"] = "oke"
            output["page"] = args['p']
            output["total_page"] = 6 # round(Transaction_Details.count()/args['rp'])
            output["per_page"] = args['rp']
            output["data"] = rows
            
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
                return {"status": "oke", "data":marshal(qry, Transaction_Details.respond_field)}, 200, {'Content-Text':'application/json'} 
        return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}

    @jwt_required
    def post(self):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'user':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        parser = reqparse.RequestParser()
        # Bagaimana menghandle tranasaction_id
        # parser.add_argument('transaction_id', location = 'json')
        parser.add_argument('product_id', location = 'json')
        parser.add_argument('qty', type = int, location = 'json')
        args = parser.parse_args()

        # get product price
        product_id = args['product_id']
        qry = Products.query.get(product_id)
        price = qry.price

        # Tambahan
        # if args["qty"] > int(qry.qty) :
        #     return {"status": "Jumlah Produk Kurang"}, 404, {'Content-Text':'application/json'}
        # sisa_qty = qry.qty - args["qty"]
        # qry.qty = sisa_qty
        # Akhir dari Tambahan


        # get transcation id
        user_id = jwtClaims["id"]
        transaction = Transactions.query.filter_by(user_id=user_id).order_by(Transactions.id.desc()).first()
        if transaction is None or transaction.status_pembayaran is True:
            transaction = Transactions(None, user_id, None, None, False)
            db.session.add(transaction)
            transaction = Transactions.query.filter_by(user_id=user_id).order_by(Transactions.id.desc()).first()
        transaction_id = transaction.id

        #save data
        transaction_detail = Transaction_Details(None, transaction_id, args['product_id'], args['qty'], price)
        db.session.add(transaction_detail)
        db.session.commit()
        newqry = Transaction_Details.query.filter_by(transaction_id=transaction_id).order_by(Transaction_Details.id.desc()).first()
        return {"status": "oke", "data":marshal(newqry, Transaction_Details.respond_field)}, 200, {'Content-Text':'application/json'}

    @jwt_required
    def put(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'user':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        parser = reqparse.RequestParser()
        # yang bisa di ganti cuma jumlahnya aja
        # parser.add_argument('product_id', location = 'json')
        parser.add_argument('qty', location = 'json')
        args = parser.parse_args()

        # product_id = args['product_id']
        # qry = Products.query.get(product_id)
        # price = qry.price
        # print(price)

        newqry = Transaction_Details.query.get(id)
        if newqry is None:
            return {"status": "NOT_FOUND"}, 404, {'Content-Text':'application/json'}
        
        # if args['product_id'] is not None:
        #     # Tambahan
        #     product_id = newqry.product_id
        #     qry = Products.query.get(product_id)
        #     qry.qty = qry.qty + newqry.qty
            # Akhir dari Tambahan

            # newqry.product_id = args['product_id']
            # newqry.price = price

        if args['qty'] is not None:
            newqry.qty = args['qty']
        
        db.session.commit()
        return {"status": "oke", "data":marshal(newqry, Transaction_Details.respond_field)}, 200, {'Content-Text':'application/json'}    
    
    @jwt_required
    def delete(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims["status"] != "user":
            return {"status": "NOT_FOUND"}, 404, {'Content-Text':'application/json'}
        
        qry = Transaction_Details.query.get(id)
        if qry is None:
            return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}
        # Tambahan 
        # product_id = qry.product_id
        # product_qry = Products.query.get(product_id)
        # product_qry.qty = product_qry.qty + qry.qty
        # Akhir dari Tambahan

        db.session.delete(qry)
        db.session.commit()
        return {"status": "oke", "data":marshal(qry, Transaction_Details.respond_field)}, 200, {'Content-Text':'application/json'}

api.add_resource(UserTransactionDetailsResource, '/user/transaction_detail', '/user/transaction_detail/<int:id>')

#Resource User Table Transaction Details
# BUAT PENGEMBANGAN # CLEAR
class UserTransactionsResource(Resource):

    @jwt_required
    def get(self, id = None):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'user':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        user_id = jwtClaims['id']
        
        if id is None:
            parser = reqparse.RequestParser()
            parser.add_argument('p', type=int, location = 'args', default = 1)
            parser.add_argument('rp', type=int, location = 'args', default = 5)

            args = parser.parse_args()

            offset = (args['p'] * args['rp']) - args['rp']
            
            output = dict()
            qry = Transactions.query.filter_by(user_id = user_id)
                
            rows = []
            for row in qry.limit(args['rp']).offset(offset).all():
                rows.append(marshal(row, Transactions.respond_field))
            
            output["status"] = "oke"
            output["page"] = args['p']
            output["total_page"] = 6 # round(Transactions.count()/args['rp'])
            output["per_page"] = args['rp']
            output["data"] = rows
            
            return output, 200, {'Content-Text':'application/json'}
        else:
            qry = Transactions.query.filter_by(user_id = user_id).get(id)
            output = dict()
            if qry is not None:
                output["status"] = "oke"
                # output["page"] = args['p']
                # output["total_page"] = 6 # round(len(Ta)/args['rp'])
                # output["per_page"] = args['rp']
                output["hasil"] = marshal(qry, Transactions.respond_field)
                return output, 200, {'Content-Text':'application/json'} 
        return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}

    @jwt_required
    def post(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'user':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}
        
        username = jwtClaims['username']
        
        parser = reqparse.RequestParser()
        parser.add_argument('code_pembayaran', location = 'json')
        args = parser.parse_args()

        newqry = Transactions.query.get(id)
        if newqry is None:
            return {"status": "NOT_FOUND"}, 404, {'Content-Text':'application/json'}
        print("BEFORE", newqry.status_pembayaran)
        if args['code_pembayaran'] == (username + '123') and newqry.status_pembayaran == False:
            newqry.status_pembayaran = True
        elif newqry.status_pembayaran == True:
            return {"status": "Pembayaran telah dilunasi sebelumnya"}, 200, {'Content-Text':'application/json'}    

        db.session.commit()
        print("AFTER", newqry.status_pembayaran)
        return {"status": "Payment Success", "data":marshal(newqry, Transactions.respond_field)}, 200, {'Content-Text':'application/json'}
    
    @jwt_required
    def delete(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims["status"] != "user":
            return {"status": "NOT_FOUND"}, 404, {'Content-Text':'application/json'}
        
        qry = Transactions.query.get(id)
        # newqry = Transaction_Details.query.filter_by(transaction_id=id)
        if qry is None:
            return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}
        if qry.status_pembayaran == False:
            db.session.delete(qry)
        # if newqry is not None:
        #     for qry in newqry.all():
        #         db.session.delete(qry)
            db.session.commit()
            return {"status": "oke", "data":marshal(qry,Transactions.respond_field)}, 200, {'Content-Text':'application/json'}

api.add_resource(UserTransactionsResource, '/user/transaction', '/user/transaction/<int:id>')

"""
SINGLE TRANSACTION
class UserTransactionsResource(Resource):

    @jwt_required
    def get(self, id = None):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'user':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        user_id = jwtClaims['id']
        
        if id is None:
            parser = reqparse.RequestParser()
            parser.add_argument('p', type=int, location = 'args', default = 1)
            parser.add_argument('rp', type=int, location = 'args', default = 5)

            args = parser.parse_args()

            offset = (args['p'] * args['rp']) - args['rp']
            
            output = dict()
            qry = Transactions.query.filter_by(user_id = user_id)
                
            rows = []
            for row in qry.limit(args['rp']).offset(offset).all():
                rows.append(marshal(row, Transactions.respond_field))
            output["status"] = "oke"
            output["page"] = args['p']
            output["total_page"] = 6 # round(Transactions.count()/args['rp'])
            output["per_page"] = args['rp']
            output["data"] = rows
            
            return output, 200, {'Content-Text':'application/json'}
        else:
            qry = Transactions.query.filter_by(user_id = user_id).get(id)
            output = dict()
            if qry is not None:
                output["status"] = "oke"
                output["page"] = args['p']
                output["total_page"] = 6 # round(len(Ta)/args['rp'])
                output["per_page"] = args['rp']
                output["data"] = marshal(qry, Transactions.respond_field)
                return output, 200, {'Content-Text':'application/json'} 
        return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}

    @jwt_required
    def post(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'user':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        user_id = jwtClaims['id']

        parser = reqparse.RequestParser()
        parser.add_argument('product_id', location = 'json')
        parser.add_argument('qty', location = 'json')
        args = parser.parse_args()
        # id, user_id, product_id, qty, price, total_price, status_pembayaran
        # Get data and update data in Products
        qry = Products.query.get(args["product_id"])
        price = qry.price
        total_price = price * args["qty"]
        qry.qty = qry.qty - args["qty"]

        transaction = Transactions(
            None, user_id, args['product_id'], args['qty'], price, total_price, 'False'
            )
        db.session.add(transaction)
        db.session.commit()
        return {"status": "Add Success", "data":transaction}, 200, {'Content-Text':'application/json'}

    @jwt_required
    def put(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'user':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}
        
        user_id = jwt_required["id"]

        parser = reqparse.RequestParser()
        parser.add_argument('product_id', location = 'json')
        parser.add_argument('qty', location = 'json')
        args = parser.parse_args()

        # get data from Transactions and check it
        qry = Transactions.query.get(id)
        if qry is None:
            return {"status": "NOT_FOUND"}, 404, {'Content-Text':'application/json'}
        
        if qry.status_pembayaran == "True":
            return {"status": "Can't change data"}, 404, {'Content-Text':'application/json'}
        
        # get data from Products and update it
        # change the old
        product = Products.query.get(qry.product_id)
        product.qty = product.qty + qry.qty

        if args['product_id'] is not None:
            newproduct = Products.query.get(args['product_id'])
            qry.product_id = args['product_id']
            price = newproduct.price
            qry.price = price

            if args['qty'] is not None:
                newproduct.qty = newproduct.qty - args['qty']
                qry.qty = args['qty']
            else:
                newproduct.qty = newproduct.qty - qry.qty
        else:
            if args['qty'] is not None:
                qry.qty = args['qty']
                product.qty = product.qty + args['qty']
        
        db.session.commit()
        return {"status": "Success Updated"}, 200, {'Content-Text':'application/json'}    
    
    @jwt_required
    def delete(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims["status"] != "user":
            return {"status": "NOT_FOUND"}, 404, {'Content-Text':'application/json'}
        
        qry = Transactions.query.get(id)
        # newqry = Transaction_Details.query.filter_by(transaction_id=id)
        if qry is None:
            return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}

        if qry.status_pembayaran == "True":
            return {"status": "Can't change data"}, 404, {'Content-Text':'application/json'}

        # get and change Products
        product_id = qry.product_id
        product = Products.query.get(product_id)
        product.qty = product.qty + qry.qty

        db.session.delete(qry)
        # if newqry is not None:
        #     for qry in newqry.all():
        #         db.session.delete(qry)
        db.session.commit()
        return {"status": "Success deleted"}, 200, {'Content-Text':'application/json'}

api.add_resource(UserTransactionsResource, '/user/transaction', '/user/transaction/<int:id>')


class Tambahan(Resource):

    @jwt_required
    def post(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'user':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}
        
        username = jwtClaims['username']
        
        parser = reqparse.RequestParser()
        parser.add_argument('code_pembayaran', location = 'json')
        args = parser.parse_args()

        newqry = Transactions.query.get(id)
        if newqry is None:
            return {"status": "NOT_FOUND"}, 404, {'Content-Text':'application/json'}
        
        if args['code_pembayaran'] == (username + '123') and newqry.status_pembayaran == "False":
            newqry.status_pembayaran = "True"
        elif newqry.status_pembayaran == "True":
            return {"status": "Pembayaran telah dilunasi sebelumnya"}, 200, {'Content-Text':'application/json'}    

        db.session.commit()
        return {"status": "Payment Success"}, 200, {'Content-Text':'application/json'}

api.add_resource(Tambahan, '/user/transaction/pembayaran/<int:id>')

"""