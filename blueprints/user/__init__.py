from blueprints import db
from flask_restful import fields

"""
# Minimum Transactions db
class Transactions(db.Model):
    
    __tablename__ = "Transactions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    user_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)
    # payment_method_id = db.Column(db.Integer)
    # shipping_method_id = db.Column(db.Integer)
    qty = db.Column(db.Integer)
    price = db.Column(db.Integer)
    total_price = db.Column(db.Integer)
    status_pembayaran = db.Column(db.String(255))
    # created_at = db.Column(db.DataTime)
    # updated_at = db.Column(db.DataTime)
    # deleted_at = db.Column(db.DataTime)

    respond_field = {
        'id' : fields.Integer,
        'user_id' : fields.Integer,
        'product_id' : fields.Integer,
        # 'payment_method_id' : fields.Integer,
        # 'shipping_method_id' : fields.Integer,
        'qty' : fields.Integer,
        'price' : fields.Integer,
        'total_price' : fields.Integer,
        'status_pembayaran' : fields.String
        # 'created_at' : fields.DataTime,
        # 'updated_at' : fields.DataTime,
        # 'deleted_at' : fields.DataTime
    }

    # , payment_method_id, shipping_method_id
    def __init__(self, id, user_id, product_id, qty, price, total_price, status_pembayaran): # created_at, updated_at, deleted_at
        self.id = id
        self.user_id = user_id
        self.product_id = user_id
        # self.payment_method_id = payment_method_id
        # self.shipping_method_id = shipping_method_id
        self.qty = qty
        self.price = price
        self.total_price = total_price
        self.status_pembayaran = status_pembayaran
        # self.created_at = created_at
        # self.updated_at = updated_at
        # self.deleted_at = deleted_at
        

    def __repr__(self):
        return '<Transactions %r>' % self.id

# Pengembangan
"""

class Transactions(db.Model):

    __tablename__ = "Transactions"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    user_id = db.Column(db.Integer)
    total_qty = db.Column(db.Integer)
    total_price = db.Column(db.Integer)
    status_pembayaran = db.Column(db.String(255))
    # created_at = db.Column(db.DataTime)
    # updated_at = db.Column(db.DataTime)
    # deleted_at = db.Column(db.DataTime)

    respond_field = {
        'id' : fields.Integer,
        'user_id' : fields.Integer,
        'total_qty' : fields.Integer,
        'total_price' : fields.Integer,
        'status_pembayaran' : fields.String
        # 'created_at' : fields.DataTime,
        # 'updated_at' : fields.DataTime,
        # 'deleted_at' : fields.DataTime
    }

    def __init__(self, id, user_id, total_qty, total_price, status_pembayaran): # created_at, updated_at, deleted_at
        self.id = id
        self.user_id = user_id
        self.total_qty = total_qty
        self.total_price = total_price
        self.status_pembayaran = status_pembayaran
        # self.created_at = created_at
        # self.updated_at = updated_at
        # self.deleted_at = deleted_at
        

    def __repr__(self):
        return '<Transactions %r>' % self.id

class Transaction_Details(db.Model):

    __tablename__ = "Transaction_Details"

    id = db.Column(db.Integer, primary_key = True, autoincrement=True, unique=True, nullable=False)
    transaction_id = db.Column(db.String(255))
    product_id = db.Column(db.Integer)
    qty = db.Column(db.Integer)
    price = db.Column(db.Integer)
    # created_at = db.Column(db.DataTime)
    # updated_at = db.Column(db.DataTime)
    # deleted_at = db.Column(db.DataTime)

    respond_field = {
        'id' : fields.Integer,
        'transaction_id' : fields.String,
        'product_id' : fields.Integer,
        'qty' : fields.Integer,
        'price' : fields.Integer
        # 'created_at' : fields.DataTime,
        # 'updated_at' : fields.DataTime,
        # 'deleted_at' : fields.DataTime
    }

    def __init__(self, id, transaction_id, product_id, qty, price): #created_at, updated_at, deleted_at
        self.id = id
        self.transaction_id = transaction_id
        self.product_id = product_id
        self.qty = qty
        self.price = price
        # self.created_at = created_at
        # self.updated_at = updated_at
        # self.deleted_at = deleted_at

    def __repr__(self):
        return '<Transactions_Details %r>' %self.id