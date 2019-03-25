import logging, json
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from blueprints import db
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints.auth import *
from blueprints.client import *
from blueprints.user import *
import math as ma
from flask_cors import CORS
from . import *

bp_user = Blueprint('User', __name__)
CORS(bp_user)
api = Api(bp_user)

# Bagian Resource untuk Users (#CLEAR)
class UserResource(Resource):

    @jwt_required
    def get(self):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] not in ['user', 'client']:
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

        if jwtClaims['status']  not in ['user', 'client']:
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        parser = reqparse.RequestParser()
        parser.add_argument('username', location = 'json')
        parser.add_argument('password', location = 'json')
        parser.add_argument('email', location = 'json')
        parser.add_argument('lokasi', location = 'json')
        args = parser.parse_args()

        user_id = jwtClaims["id"]
        qry = Users.query.get(user_id)
        if qry is None:
            return {"status": "Your Account is deleted by your self"}, 404, {'Content-Text':'application/json'}
        
        if args['username'] is not None:
            qry.username = args['username']
        if args['lokasi'] is not None:
            qry.lokasi = args['lokasi']
        if args['email'] is not None:
            qry.email = args['email']
        if args['password'] is not None:
            qry.password = args["password"]
        
        db.session.commit()
        return {"status": "oke", 'data':marshal(qry, Users.respond_field)}, 200, {'Content-Text':'application/json'}
    
    @jwt_required
    def delete(self):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status']  not in ['user', 'client']:
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}
        
        user_id = jwtClaims["id"]
        qry = Users.query.get(user_id)
        
        if qry is None:
            return {"status": "Your Account is deleted by your self"}, 404, {'Content-Text':'application/json'}

        db.session.delete(qry)
        db.session.commit()
        return {"status": "oke", 'data':marshal(qry, Users.respond_field)}, 200, {'Content-Text':'application/json'}

api.add_resource(UserResource, '/user')

class UserTransactionDetailsResource(Resource):

    @jwt_required
    def get(self, id = None):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'user':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        # user_id = jwtClaims['id']
        #Transaction detail dari transaksi terakhir
        if id is None:
            parser = reqparse.RequestParser()
            parser.add_argument('p', type=int, location = 'args', default = 1)
            parser.add_argument('rp', type=int, location = 'args', default = 20)

            args = parser.parse_args()

            offset = (args['p'] * args['rp']) - args['rp']
            
            output = dict()
            user_id = jwtClaims["id"]
            qry = Transactions.query.filter_by(user_id = user_id).order_by(Transactions.id.desc()).first()
            td_qry = Transaction_Details.query.filter_by(transaction_id = qry.id)

            rows = []
            total_page = 0
            for row in td_qry.limit(args['rp']).offset(offset).all():
                product_id = row.product_id
                product_qry = Products.query.get(product_id)
                nama_produk = product_qry.nama
                url_gambar = product_qry.url_picture

                product_type_id = product_qry.product_type_id
                pt_qry = Product_Types.query.get(product_type_id)
                kategori_produk = pt_qry.nama
                tambahan = dict()
                tambahan['nama_produk'] = nama_produk
                tambahan["url_gambar"] = url_gambar
                tambahan["kategori_produk"] = kategori_produk
                rows.append({"ori":marshal(row, Transaction_Details.respond_field), "tambahan": tambahan})
                # total_page = total_page + 1

            output["status"] = "oke"
            output["page"] = args['p']
            output["total_page"] = ma.floor(total_page/2) # 6 round(Transaction_Details.count()/args['rp'])
            output["per_page"] = args['rp']
            output["data"] = rows
            
            return output, 200, {'Content-Text':'application/json'}
        else:
            qry = Transaction_Details.query.filter_by(transaction_id = id)
            if qry is None:
                return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}

            rows = []
            for row in qry.all():
                rows.append(marshal(row, Transaction_Details.respond_field))
            return {"status": "oke", "data":rows}, 200, {'Content-Text':'application/json'} 
        return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}

    @jwt_required
    def post(self):
        jwtClaims = get_jwt_claims()
        if jwtClaims['status'] != 'user':
            return {"status": "Invalid Status"}, 404, {'Content-Text':'application/json'}

        parser = reqparse.RequestParser()
        # Bagaimana menghandle transaction_id
        # parser.add_argument('transaction_id', location = 'json')
        parser.add_argument('product_id', type = int, location = 'json')
        parser.add_argument('qty', type = int, location = 'json')
        args = parser.parse_args()

        # get product price
        product_id = args['product_id']
        qry = Products.query.get(product_id)
        price = qry.price

        # add point
        qry.point = qry.point + 1
        kategori = Product_Types.query.get(qry.product_type_id)
        kategori.point = kategori.point + 1

        # set new qty for Product
        if args["qty"] > int(qry.qty) :
            return {"status": "Jumlah Produk Kurang"}, 404, {'Content-Text':'application/json'}
        sisa_qty = qry.qty - args["qty"]
        qry.qty = sisa_qty

        # get transcation id
        user_id = jwtClaims["id"]
        transaction = Transactions.query.filter_by(user_id=user_id).order_by(Transactions.id.desc()).first()
        if transaction is None or transaction.status_pembayaran == 'Lunas':
            transaction = Transactions(None, user_id, 0, 0, "Belum Lunas")
            db.session.add(transaction)
            # db.session.commit()
            transaction = Transactions.query.filter_by(user_id=user_id).order_by(Transactions.id.desc()).first()
        
        transaction_id = transaction.id
        # transaction_total_qty = transaction.total_qty
        # transaction_total_price = transaction.total_price
        transaction.total_qty = transaction.total_qty + args["qty"]
        transaction.total_price = transaction.total_price + (args["qty"]*price)

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
        parser.add_argument('qty', type=int, location = 'json')
        args = parser.parse_args()

        # product_id = args['product_id']
        # qry = Products.query.get(product_id)
        # price = qry.price
        # print(price)

        qry = Transaction_Details.query.get(id)
        if qry is None:
            return {"status": "NOT_FOUND"}, 404, {'Content-Text':'application/json'}
        
        # get qty from product and set it back
        product_id = qry.product_id
        product = Products.query.get(product_id)

        transaction_id = qry.transaction_id
        transaction = Transactions.query.get(transaction_id)
        if transaction.status_pembayaran == "Lunas":
            return {"status": "Data tidak bisa di edit"}, 404, {'Content-Text':'application/json'}
        
        selisih = qry.qty - args['qty']
        sisa_di_prod = product.qty + selisih
        if sisa_di_prod>=0:
            product.qty = sisa_di_prod
            transaction.total_qty = transaction.total_qty + (args['qty'] - qry.qty)
            transaction.total_price = transaction.total_price + (product.price * (args['qty'] - qry.qty))
            qry.qty = args['qty']
        else:
            return {"status": "Jumlah Produk Kurang"}, 404, {'Content-Text':'application/json'}
        db.session.commit()
        return {"status": "oke", "data":marshal(qry, Transaction_Details.respond_field)}, 200, {'Content-Text':'application/json'}    
    
    @jwt_required
    def delete(self, id):
        jwtClaims = get_jwt_claims()
        if jwtClaims["status"] != "user":
            return {"status": "NOT_FOUND"}, 404, {'Content-Text':'application/json'}
        
        qry = Transaction_Details.query.get(id)
        if qry is None:
            return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}
        
        # edit transaction
        transaction = Transactions.query.get(qry.transaction_id)
        if transaction.status_pembayaran == "Lunas":
            return {"status": "Data tidak bisa di edit"}, 404, {'Content-Text':'application/json'}

        transaction.total_qty = transaction.total_qty - qry.qty
        transaction.total_price = transaction.total_price - (qry.qty * qry.price)

        # Adding qty in product
        product_id = qry.product_id
        product_qry = Products.query.get(product_id)
        product_qry.qty = product_qry.qty + qry.qty

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
            total_pages = 0
            for row in qry.limit(args['rp']).offset(offset).all():
                rows.append(marshal(row, Transactions.respond_field))
                total_pages = total_pages + 1

            output["status"] = "oke"
            output["page"] = args['p']
            output["total_page"] = ma.ceil(total_pages/args['rp']) #6 # round(Transactions.count()/args['rp'])
            output["per_page"] = args['rp']
            output["data"] = rows
            
            return output, 200, {'Content-Text':'application/json'}
        else:
            # qry = Transactions.query.filter_by(user_id = user_id).filter_by(transaction_id=id)
            qry = Transactions.query.filter_by(user_id = user_id).get(id)
            output = dict()
            if qry is not None:
                output["status"] = "oke"
                # output["page"] = args['p']
                # output["total_page"] = 6 # round(len(Ta)/args['rp'])
                # output["per_page"] = args['rp']
                output["data"] = marshal(qry, Transactions.respond_field)
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
        # print("BEFORE", newqry.status_pembayaran)
        if args['code_pembayaran'] == (username + '123') and newqry.status_pembayaran == "Belum Lunas":
            newqry.status_pembayaran = "Lunas"
        elif newqry.status_pembayaran == "Lunas":
            return {"status": "Pembayaran telah dilunasi sebelumnya"}, 200, {'Content-Text':'application/json'}    

        db.session.commit()
        # print("AFTER", newqry.status_pembayaran)
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
        if qry.status_pembayaran == "Belum Lunas":
            td_qry = Transaction_Details.query.filter_by(transaction_id=id)
            for row in td_qry.all():
                product_id = row.product_id
                product = Products.query.get(product_id)
                product.qty = product.qty + row.qty
                db.session.delete(row)
            db.session.delete(qry)
        # if newqry is not None:
        #     for qry in newqry.all():
        #         db.session.delete(qry)
            db.session.commit()
            return {"status": "oke", "data":marshal(qry,Transactions.respond_field)}, 200, {'Content-Text':'application/json'}
        return {"status": "DATA_NOT_FOUND"}, 404, {'Content-Text':'application/json'}

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