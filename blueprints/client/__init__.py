from blueprints import db
from flask_restful import fields

# Database untuk barang yang dijual 
class Products(db.Model):

    __tablename__="Products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    nama = db.Column(db.String(255), nullable=False)
    # buat deskripsi, nanti di cari tahu lagi
    deskripsi = db.Column(db.Text)
    product_type_id = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    satuan = db.Column(db.String(255), nullable = False)
    status = db.Column(db.String(255), nullable=False)
    url_picture = db.Column(db.Text)
    qty = db.Column(db.Integer, nullable=False)
    # berat = db.Column(db.Integer) pindah ke product_descriptions
    client_id = db.Column(db.Integer, nullable=False)
    lokasi = db.Column(db.String(50))
    point = db.Column(db.Integer)
    # created_at = db.Column(db.DataTime)
    # updated_at = db.Column(db.DataTime)
    # deleted_at = db.Column(db.DataTime)

    respond_field = {
        'id' : fields.Integer,
        'nama' : fields.String,
        # buat deskripsi, nanti di cari tahu lagi
        'deskripsi' : fields.String,
        'product_type_id' : fields.Integer,
        'price' : fields.Integer,
        'satuan' : fields.String,
        'status' : fields.String,
        'url_picture' : fields.String,
        'qty' : fields.Integer,
        # 'berat' : fields.Integer,
        'client_id' : fields.Integer,
        'lokasi': fields.String,
        'point' : fields.String
        # 'created_at' : fields.DataTime,
        # 'updated_at' : fields.DataTime,
        # 'deleted_at' : fields.DataTime
        }

    def __init__(
        self, id, nama, deskripsi, product_type_id, price, satuan, status, url_picture, qty, client_id,
        lokasi, point): # created_at, updated_at, deleted_at
        self.id = id
        self.nama = nama
        self.deskripsi = deskripsi
        self.product_type_id = product_type_id
        self.price = price
        self.satuan = satuan
        self.status = status
        self.url_picture = url_picture
        self.qty = qty
        self.client_id = client_id
        self.lokasi = lokasi
        self.point = point
        # self.created_at = created_at
        # self.updated_at = updated_at
        # self.deleted_at = deleted_at
        
    def __repr__(self):
        return '<Products %r>' % self.id

class Product_Types(db.Model):

    __tablename__="Product_Types"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    nama = db.Column(db.String(255), nullable=False)
    point = db.Column(db.Integer)
    # created_at = db.Column(db.DataTime)
    # updated_at = db.Column(db.DataTime)
    # deleted_at = db.Column(db.DataTime)

    respond_field = {
        'id' : fields.Integer,
        'nama' : fields.String,
        'point' : fields.String
        # 'created_at' : fields.DataTime,
        # 'updated_at' : fields.DataTime,
        # 'deleted_at' : fields.DataTime
        }

    def __init__(
        self, id, nama, point
        ): # created_at, updated_at, deleted_at
        self.id = id
        self.nama = nama
        self.point = point
        # self.created_at = created_at
        # self.updated_at = updated_at
        # self.deleted_at = deleted_at
        
    def __repr__(self):
        return '<Product_Types %r>' % self.id