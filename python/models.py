from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Модель користувача"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='client')  # guest, client, admin
    avatar = db.Column(db.String(200), default='default-avatar.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Зв'язки
    configurations = db.relationship('Configuration', backref='user', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'avatar': self.avatar,
            'created_at': self.created_at.isoformat()
        }

class Category(db.Model):
    """Модель категорії товарів"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50), default='cpu')
    image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Зв'язки
    products = db.relationship('Product', backref='category', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'icon': self.icon,
            'image': self.image
        }

class Product(db.Model):
    """Модель товару"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float)
    image = db.Column(db.String(200), default='placeholder.png')
    gallery = db.Column(db.Text)  # JSON array of images
    specs = db.Column(db.Text)  # JSON object with specifications
    description = db.Column(db.Text)
    stock = db.Column(db.Integer, default=0)
    brand = db.Column(db.String(100))
    compatibility = db.Column(db.Text)  # JSON array of compatible components
    featured = db.Column(db.Boolean, default=False)
    bestseller = db.Column(db.Boolean, default=False)
    new = db.Column(db.Boolean, default=False)
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_specs(self):
        if self.specs:
            try:
                return json.loads(self.specs)
            except:
                return {}
        return {}
    
    def set_specs(self, specs_dict):
        self.specs = json.dumps(specs_dict, ensure_ascii=False)
    
    def get_compatibility(self):
        if self.compatibility:
            try:
                return json.loads(self.compatibility)
            except:
                return []
        return []
    
    def set_compatibility(self, comp_list):
        self.compatibility = json.dumps(comp_list, ensure_ascii=False)
    
    def get_gallery(self):
        if self.gallery:
            try:
                return json.loads(self.gallery)
            except:
                return []
        return []
    
    def set_gallery(self, gallery_list):
        self.gallery = json.dumps(gallery_list, ensure_ascii=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'category_id': self.category_id,
            'category': self.category.name if self.category else None,
            'price': self.price,
            'old_price': self.old_price,
            'image': self.image,
            'gallery': self.get_gallery(),
            'specs': self.get_specs(),
            'description': self.description,
            'stock': self.stock,
            'brand': self.brand,
            'compatibility': self.get_compatibility(),
            'featured': self.featured,
            'bestseller': self.bestseller,
            'new': self.new,
            'views': self.views
        }

class Configuration(db.Model):
    """Модель збереженої конфігурації ПК"""
    __tablename__ = 'configurations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    components = db.Column(db.Text)  # JSON object with component_id for each slot
    total_price = db.Column(db.Float, default=0)
    compatibility_status = db.Column(db.String(20), default='unknown')  # compatible, incompatible, unknown
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_components(self):
        if self.components:
            try:
                return json.loads(self.components)
            except:
                return {}
        return {}
    
    def set_components(self, components_dict):
        self.components = json.dumps(components_dict, ensure_ascii=False)
    
    def calculate_total(self, products):
        total = 0
        components = self.get_components()
        for slot, product_id in components.items():
            if product_id:
                product = next((p for p in products if p.id == product_id), None)
                if product:
                    total += product.price
        return total
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'components': self.get_components(),
            'total_price': self.total_price,
            'compatibility_status': self.compatibility_status,
            'created_at': self.created_at.isoformat()
        }

class Order(db.Model):
    """Модель замовлення"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    config_id = db.Column(db.Integer, db.ForeignKey('configurations.id'))
    items = db.Column(db.Text)  # JSON array of order items
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, processing, shipped, delivered, cancelled
    payment_method = db.Column(db.String(50))
    delivery_address = db.Column(db.Text)
    contact_phone = db.Column(db.String(20))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Зв'язок
    configuration = db.relationship('Configuration', backref='order')
    
    def get_items(self):
        if self.items:
            try:
                return json.loads(self.items)
            except:
                return []
        return []
    
    def set_items(self, items_list):
        self.items = json.dumps(items_list, ensure_ascii=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'config_id': self.config_id,
            'items': self.get_items(),
            'total_price': self.total_price,
            'status': self.status,
            'payment_method': self.payment_method,
            'delivery_address': self.delivery_address,
            'contact_phone': self.contact_phone,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

class CartItem(db.Model):
    """Модель елемента кошика (для збереження в БД)"""
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    is_configuration = db.Column(db.Boolean, default=False)
    configuration_id = db.Column(db.Integer, db.ForeignKey('configurations.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Зв'язки
    product = db.relationship('Product', backref='cart_items')
    configuration = db.relationship('Configuration', backref='cart_items')
