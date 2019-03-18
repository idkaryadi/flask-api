from blueprints import db
from flask_restful import fields

# Database untuk barang yang dijual 
class Products(db.Model):

    __tablename__="Products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    nama = db.Column(db.String(255), nullable=False)
    # vendor = db.Column(db.String(255))
    # buat deskripsi, nanti di cari tahu lagi
    deskripsi = db.Column(db.Text)
    product_type_id = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(255))
    url_picture = db.Column(db.String(255))
    qty = db.Column(db.Integer, nullable=False)
    # berat = db.Column(db.Integer) pindah ke product_descriptions
    client_id = db.Column(db.Integer, nullable=False)
    # created_at = db.Column(db.DataTime)
    # updated_at = db.Column(db.DataTime)
    # deleted_at = db.Column(db.DataTime)

    respond_field = {
        'id' : fields.Integer,
        'nama' : fields.String,
        # 'vendor' : fields.String,
        # buat deskripsi, nanti di cari tahu lagi
        'deskripsi' : fields.String,
        'product_type_id' : fields.Integer,
        'price' : fields.Integer,
        'status' : fields.String,
        'url_picture' : fields.String,
        'qty' : fields.Integer,
        # 'berat' : fields.Integer,
        'client_id' : fields.Integer
        # 'created_at' : fields.DataTime,
        # 'updated_at' : fields.DataTime,
        # 'deleted_at' : fields.DataTime
        }

    def __init__(
        self, id, nama, deskripsi, product_type_id, price, status, url_picture, qty, client_id
        ): # created_at, updated_at, deleted_at
        self.id = id
        self.nama = nama
        # self.vendor = vendor
        self.deskripsi = deskripsi
        self.product_type_id = product_type_id
        self.price = price
        self.status = status
        self.url_picture = url_picture
        self.qty = qty
        self.client_id = client_id
        # self.created_at = created_at
        # self.updated_at = updated_at
        # self.deleted_at = deleted_at
        
    def __repr__(self):
        return '<Products %r>' % self.id

class Product_Types(db.Model):

    __tablename__="Product_Types"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    nama = db.Column(db.String(255), nullable=False)
    # created_at = db.Column(db.DataTime)
    # updated_at = db.Column(db.DataTime)
    # deleted_at = db.Column(db.DataTime)

    respond_field = {
        'id' : fields.Integer,
        'nama' : fields.String
        # 'created_at' : fields.DataTime,
        # 'updated_at' : fields.DataTime,
        # 'deleted_at' : fields.DataTime
        }

    def __init__(
        self, id, nama
        ): # created_at, updated_at, deleted_at
        self.id = id
        self.nama = nama
        # self.created_at = created_at
        # self.updated_at = updated_at
        # self.deleted_at = deleted_at
        
    def __repr__(self):
        return '<Product_Types %r>' % self.id