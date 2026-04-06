from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import os
import uuid

from config import config
from models import db, User, Category, Product, Configuration, Order
from forms import RegistrationForm, LoginForm, ProfileForm, CategoryForm, ProductForm, OrderForm, ConfigurationForm
from utils import (
    admin_required, get_cart_from_session, add_to_cart, remove_from_cart,
    update_cart_quantity, clear_cart, calculate_cart_total, get_cart_items_with_products,
    check_component_compatibility, format_price, generate_slug, create_default_admin
)

app = Flask(__name__)
app.config.from_object(config['default'])

# Ініціалізація розширень
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Будь ласка, увійдіть для доступу до цієї сторінки'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Створення таблиць та тестових даних
def init_db():
    with app.app_context():
        db.create_all()
        create_default_admin()
        create_sample_data()

def create_sample_data():
    """Створення тестових даних"""
    # Перевірка чи дані вже існують
    if Category.query.first():
        return
    
    # Категорії
    categories = [
        Category(name='Процесори (CPU)', slug='cpu', description='Найпотужніші процесори для ігрових ПК', icon='cpu'),
        Category(name='Відеокарти (GPU)', slug='gpu', description='Графічні прискорювачі для ігор та роботи', icon='gpu'),
        Category(name="Оперативна пам'ять (RAM)", slug='ram', description='Швидка оперативна пам\'ять DDR4/DDR5', icon='ram'),
        Category(name='Накопичувачі (SSD/HDD)', slug='storage', description='SSD та HDD для зберігання даних', icon='storage'),
        Category(name='Материнські плати', slug='motherboard', description='Основа вашого ПК', icon='motherboard'),
        Category(name='Блоки живлення (PSU)', slug='psu', description='Надійні блоки живлення', icon='psu'),
        Category(name='Корпуси', slug='case', description='Стильні корпуси для геймерів', icon='case'),
        Category(name='Системи охолодження', slug='cooling', description='Ефективне охолодження компонентів', icon='cooling'),
    ]
    
    for cat in categories:
        db.session.add(cat)
    db.session.commit()
    
    # Товари
    products = [
        # Процесори
        Product(name='Intel Core i9-14900K', slug='intel-core-i9-14900k', category_id=1, price=24999, brand='Intel',
                old_price=27999, stock=15, featured=True, new=True,
                specs=json.dumps({'socket': 'LGA1700', 'cores': 24, 'threads': 32, 'frequency': '6.0 GHz', 'tdp': '125W'}, ensure_ascii=False),
                description='Флагманський процесор Intel 14-го покоління для найвимогливіших ігор та завдань.'),
        
        Product(name='AMD Ryzen 9 7950X', slug='amd-ryzen-9-7950x', category_id=1, price=22999, brand='AMD',
                old_price=25999, stock=12, featured=True, bestseller=True,
                specs=json.dumps({'socket': 'AM5', 'cores': 16, 'threads': 32, 'frequency': '5.7 GHz', 'tdp': '170W'}, ensure_ascii=False),
                description='Топовий процесор AMD з архітектурою Zen 4 для максимальної продуктивності.'),
        
        Product(name='Intel Core i7-14700K', slug='intel-core-i7-14700k', category_id=1, price=15999, brand='Intel',
                stock=20, featured=True,
                specs=json.dumps({'socket': 'LGA1700', 'cores': 20, 'threads': 28, 'frequency': '5.6 GHz', 'tdp': '125W'}, ensure_ascii=False),
                description='Потужний процесор для ігрових ПК середнього рівня.'),
        
        Product(name='AMD Ryzen 7 7800X3D', slug='amd-ryzen-7-7800x3d', category_id=1, price=18999, brand='AMD',
                old_price=21999, stock=8, featured=True, new=True, bestseller=True,
                specs=json.dumps({'socket': 'AM5', 'cores': 8, 'threads': 16, 'frequency': '5.0 GHz', 'tdp': '120W', 'cache': '96MB 3D V-Cache'}, ensure_ascii=False),
                description='Процесор з технологією 3D V-Cache для неймовірної продуктивності в іграх.'),
        
        # Відеокарти
        Product(name='NVIDIA GeForce RTX 4090', slug='nvidia-geforce-rtx-4090', category_id=2, price=89999, brand='NVIDIA',
                old_price=99999, stock=5, featured=True, new=True, bestseller=True,
                specs=json.dumps({'vram': '24GB GDDR6X', 'tdp': '450W', 'cuda_cores': 16384, 'boost_clock': '2.52 GHz'}, ensure_ascii=False),
                description='Найпотужніша відеокарта для ігор у 4K та 8K роздільній здатності.'),
        
        Product(name='NVIDIA GeForce RTX 4080 Super', slug='nvidia-geforce-rtx-4080-super', category_id=2, price=54999, brand='NVIDIA',
                stock=10, featured=True,
                specs=json.dumps({'vram': '16GB GDDR6X', 'tdp': '320W', 'cuda_cores': 10240, 'boost_clock': '2.55 GHz'}, ensure_ascii=False),
                description='Відмінний вибір для ігор у 4K з максимальними налаштуваннями.'),
        
        Product(name='AMD Radeon RX 7900 XTX', slug='amd-radeon-rx-7900-xtx', category_id=2, price=49999, brand='AMD',
                old_price=54999, stock=8, featured=True,
                specs=json.dumps({'vram': '24GB GDDR6', 'tdp': '355W', 'stream_processors': 6144, 'boost_clock': '2.5 GHz'}, ensure_ascii=False),
                description='Флагманська відеокарта AMD для ентузіастів.'),
        
        Product(name='NVIDIA GeForce RTX 4070 Ti Super', slug='nvidia-geforce-rtx-4070-ti-super', category_id=2, price=34999, brand='NVIDIA',
                stock=15, featured=True, bestseller=True,
                specs=json.dumps({'vram': '16GB GDDR6X', 'tdp': '285W', 'cuda_cores': 8448, 'boost_clock': '2.61 GHz'}, ensure_ascii=False),
                description='Ідеальний баланс ціни та продуктивності для 4K ігрового ПК.'),
        
        # Оперативна пам'ять
        Product(name='G.Skill Trident Z5 RGB 32GB DDR5-6000', slug='gskill-trident-z5-rgb-32gb-ddr5-6000', category_id=3, price=4999, brand='G.Skill',
                stock=25, featured=True,
                specs=json.dumps({'type': 'DDR5', 'capacity': '32GB (2x16GB)', 'frequency': '6000 MHz', 'latency': 'CL30'}, ensure_ascii=False),
                description='Високошвидкісна оперативна пам\'ять DDR5 з RGB підсвіткою.'),
        
        Product(name='Kingston Fury Beast 32GB DDR5-5600', slug='kingston-fury-beast-32gb-ddr5-5600', category_id=3, price=3999, brand='Kingston',
                stock=30, featured=True, bestseller=True,
                specs=json.dumps({'type': 'DDR5', 'capacity': '32GB (2x16GB)', 'frequency': '5600 MHz', 'latency': 'CL36'}, ensure_ascii=False),
                description='Надійна оперативна пам\'ять для ігрових систем.'),
        
        Product(name='Corsair Vengeance RGB 64GB DDR5-5600', slug='corsair-vengeance-rgb-64gb-ddr5-5600', category_id=3, price=6999, brand='Corsair',
                old_price=7999, stock=12,
                specs=json.dumps({'type': 'DDR5', 'capacity': '64GB (2x32GB)', 'frequency': '5600 MHz', 'latency': 'CL36'}, ensure_ascii=False),
                description='Великий обсяг пам\'яті для професійних завдань та ігор.'),
        
        # Накопичувачі
        Product(name='Samsung 990 Pro 2TB NVMe', slug='samsung-990-pro-2tb-nvme', category_id=4, price=6999, brand='Samsung',
                stock=20, featured=True, bestseller=True,
                specs=json.dumps({'type': 'NVMe PCIe 4.0', 'capacity': '2TB', 'read_speed': '7450 MB/s', 'write_speed': '6900 MB/s'}, ensure_ascii=False),
                description='Найшвидший SSD для миттєвого завантаження ігор.'),
        
        Product(name='WD Black SN850X 1TB', slug='wd-black-sn850x-1tb', category_id=4, price=3999, brand='Western Digital',
                stock=25, featured=True,
                specs=json.dumps({'type': 'NVMe PCIe 4.0', 'capacity': '1TB', 'read_speed': '7300 MB/s', 'write_speed': '6600 MB/s'}, ensure_ascii=False),
                description='SSD з фірмовим контролером для геймінгу.'),
        
        # Материнські плати
        Product(name='ASUS ROG Maximus Z790 Hero', slug='asus-rog-maximus-z790-hero', category_id=5, price=18999, brand='ASUS',
                old_price=21999, stock=8, featured=True, new=True,
                specs=json.dumps({'socket': 'LGA1700', 'chipset': 'Z790', 'ram_type': 'DDR5', 'max_ram': '128GB', 'form_factor': 'ATX'}, ensure_ascii=False),
                description='Преміальна материнська плата для ентузіастів Intel.'),
        
        Product(name='MSI MEG X670E ACE', slug='msi-meg-x670e-ace', category_id=5, price=15999, brand='MSI',
                stock=6, featured=True,
                specs=json.dumps({'socket': 'AM5', 'chipset': 'X670E', 'ram_type': 'DDR5', 'max_ram': '128GB', 'form_factor': 'ATX'}, ensure_ascii=False),
                description='Топова материнська плата для платформи AMD.'),
        
        # Блоки живлення
        Product(name='Corsair RM1000x 1000W', slug='corsair-rm1000x-1000w', category_id=6, price=6999, brand='Corsair',
                stock=15, featured=True, bestseller=True,
                specs=json.dumps({'wattage': 1000, 'efficiency': '80+ Gold', 'modular': 'Full Modular'}, ensure_ascii=False),
                description='Надійний блок живлення для потужних систем.'),
        
        Product(name='Seasonic PRIME TX-1600', slug='seasonic-prime-tx-1600', category_id=6, price=12999, brand='Seasonic',
                old_price=14999, stock=5, featured=True,
                specs=json.dumps({'wattage': 1600, 'efficiency': '80+ Titanium', 'modular': 'Full Modular'}, ensure_ascii=False),
                description='Платиновий блок живлення для найвимогливіших систем.'),
        
        Product(name='be quiet! Straight Power 12 850W', slug='be-quiet-straight-power-12-850w', category_id=6, price=5499, brand='be quiet!',
                stock=18, featured=True,
                specs=json.dumps({'wattage': 850, 'efficiency': '80+ Platinum', 'modular': 'Full Modular'}, ensure_ascii=False),
                description='Тихий та ефективний блок живлення.'),
        
        # Корпуси
        Product(name='Lian Li O11 Dynamic EVO', slug='lian-li-o11-dynamic-evo', category_id=7, price=5999, brand='Lian Li',
                stock=10, featured=True,
                specs=json.dumps({'form_factor': 'ATX', 'material': 'Aluminum/Steel', 'max_gpu_length': '420mm', 'radiator_support': '360mm'}, ensure_ascii=False),
                description='Преміум корпус з чудовою вентиляцією та дизайном.'),
        
        Product(name='NZXT H7 Flow', slug='nzxt-h7-flow', category_id=7, price=3999, brand='NZXT',
                stock=12, featured=True, bestseller=True,
                specs=json.dumps({'form_factor': 'ATX', 'material': 'Steel/Tempered Glass', 'max_gpu_length': '400mm', 'radiator_support': '360mm'}, ensure_ascii=False),
                description='Стильний корпус з відмінною продуваемістю.'),
        
        Product(name='Fractal Design Torrent', slug='fractal-design-torrent', category_id=7, price=7499, brand='Fractal Design',
                old_price=8999, stock=6, featured=True, new=True,
                specs=json.dumps({'form_factor': 'ATX', 'material': 'Steel', 'max_gpu_length': '461mm', 'radiator_support': '420mm'}, ensure_ascii=False),
                description='Корпус з унікальною системою охолодження.'),
        
        # Системи охолодження
        Product(name='NZXT Kraken Z73 RGB', slug='nzxt-kraken-z73-rgb', category_id=8, price=8999, brand='NZXT',
                stock=8, featured=True, new=True,
                specs=json.dumps({'type': 'AIO Liquid', 'radiator': '360mm', 'fans': 3, 'rgb': True}, ensure_ascii=False),
                description='RGB рідинне охолодження з дисплеєм.'),
        
        Product(name='be quiet! Dark Rock Pro 4', slug='be-quiet-dark-rock-pro-4', category_id=8, price=3999, brand='be quiet!',
                stock=15, featured=True, bestseller=True,
                specs=json.dumps({'type': 'Air Cooler', 'height': '162.8mm', 'fans': 2, 'tdp': '250W'}, ensure_ascii=False),
                description='Тихий баштовий кулер для потужних процесорів.'),
        
        Product(name='Corsair iCUE H150i Elite', slug='corsair-icue-h150i-elite', category_id=8, price=7499, brand='Corsair',
                stock=10, featured=True,
                specs=json.dumps({'type': 'AIO Liquid', 'radiator': '360mm', 'fans': 3, 'rgb': True, 'software': 'iCUE'}, ensure_ascii=False),
                description='Програмована RGB система охолодження.'),
    ]
    
    for prod in products:
        db.session.add(prod)
    db.session.commit()

# Головна сторінка
@app.route('/')
def index():
    featured_products = Product.query.filter_by(featured=True).limit(8).all()
    new_products = Product.query.filter_by(new=True).limit(4).all()
    bestseller_products = Product.query.filter_by(bestseller=True).limit(4).all()
    categories = Category.query.all()
    
    return render_template('index.html',
                         featured_products=featured_products,
                         new_products=new_products,
                         bestseller_products=bestseller_products,
                         categories=categories)

# Каталог
@app.route('/catalog')
@app.route('/catalog/<slug>')
def catalog(slug=None):
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Фільтри
    category = request.args.get('category', type=int)
    brand = request.args.get('brand')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort = request.args.get('sort', 'newest')
    search = request.args.get('search', '')
    
    query = Product.query
    
    if slug:
        cat = Category.query.filter_by(slug=slug).first()
        if cat:
            query = query.filter_by(category_id=cat.id)
    
    if category:
        query = query.filter_by(category_id=category)
    
    if brand:
        query = query.filter_by(brand=brand)
    
    if min_price:
        query = query.filter(Product.price >= min_price)
    
    if max_price:
        query = query.filter(Product.price <= max_price)
    
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    
    # Сортування
    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'popular':
        query = query.order_by(Product.views.desc())
    else:  # newest
        query = query.order_by(Product.created_at.desc())
    
    products = query.paginate(page=page, per_page=per_page, error_out=False)
    categories = Category.query.all()
    
    # Отримання унікальних брендів
    brands = [p.brand for p in Product.query.with_entities(Product.brand).distinct() if p.brand]
    
    return render_template('catalog.html',
                         products=products,
                         categories=categories,
                         brands=brands,
                         current_category=category,
                         current_brand=brand,
                         current_sort=sort,
                         search_query=search)

# Сторінка товару
@app.route('/product/<slug>')
def product(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    
    # Збільшуємо лічильник переглядів
    product.views += 1
    db.session.commit()
    
    # Пов'язані товари
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id
    ).limit(4).all()
    
    return render_template('product.html',
                         product=product,
                         related_products=related_products)

# API для отримання товарів
@app.route('/api/products')
def api_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

@app.route('/api/products/<int:product_id>')
def api_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

@app.route('/api/categories')
def api_categories():
    categories = Category.query.all()
    return jsonify([c.to_dict() for c in categories])

# Конструктор ПК
@app.route('/builder')
def builder():
    categories = Category.query.all()
    # Convert Product objects to dictionaries for JSON serialization
    products_list = [p.to_dict() for p in Product.query.all()]
    products = {cat.id: [p for p in products_list if p['category_id'] == cat.id] for cat in categories}
    
    return render_template('builder.html',
                         categories=categories,
                         products=products)

@app.route('/api/compatibility', methods=['POST'])
def api_compatibility():
    data = request.get_json()
    components = data.get('components', {})
    
    products_dict = {p.id: p for p in Product.query.all()}
    result = check_component_compatibility(components, products_dict)
    
    return jsonify(result)

@app.route('/save-configuration', methods=['POST'])
@login_required
def save_configuration():
    data = request.get_json()
    
    config = Configuration(
        user_id=current_user.id,
        name=data.get('name', 'Моя конфігурація'),
        components=json.dumps(data.get('components', {}))
    )
    
    # Розрахунок ціни
    products_dict = {p.id: p for p in Product.query.all()}
    total = 0
    for product_id in data.get('components', {}).values():
        if product_id:
            product = products_dict.get(int(product_id))
            if product:
                total += product.price
    
    config.total_price = total
    db.session.add(config)
    db.session.commit()
    
    return jsonify({'success': True, 'config_id': config.id})

# Кошик
@app.route('/cart')
def cart():
    cart_items = get_cart_from_session(session)
    products = Product.query.all()
    items_with_products = get_cart_items_with_products(cart_items, products)
    total = calculate_cart_total(cart_items, products)
    
    return render_template('cart.html',
                         items=items_with_products,
                         total=total)

@app.route('/api/cart/add', methods=['POST'])
def api_add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id:
        return jsonify({'success': False, 'message': 'Не вказано товар'})
    
    cart = add_to_cart(session, product_id, quantity)
    
    product = Product.query.get(product_id)
    
    return jsonify({
        'success': True,
        'cart_count': sum(item['quantity'] for item in cart.values()),
        'message': f'{product.name} додано до кошика' if product else 'Товар додано'
    })

@app.route('/api/cart/remove', methods=['POST'])
def api_remove_from_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({'success': False, 'message': 'Не вказано товар'})
    
    cart = remove_from_cart(session, product_id)
    
    return jsonify({
        'success': True,
        'cart_count': sum(item['quantity'] for item in cart.values())
    })

@app.route('/api/cart/update', methods=['POST'])
def api_update_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id:
        return jsonify({'success': False, 'message': 'Не вказано товар'})
    
    cart = update_cart_quantity(session, product_id, quantity)
    
    products = Product.query.all()
    total = calculate_cart_total(cart, products)
    
    return jsonify({
        'success': True,
        'cart_count': sum(item['quantity'] for item in cart.values()),
        'total': total
    })

@app.route('/api/cart/clear', methods=['POST'])
def api_clear_cart():
    clear_cart(session)
    return jsonify({'success': True})

# Оформлення замовлення
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart_items = get_cart_from_session(session)
    
    if not cart_items:
        flash('Ваш кошик порожній', 'warning')
        return redirect(url_for('cart'))
    
    products = Product.query.all()
    items_with_products = get_cart_items_with_products(cart_items, products)
    total = calculate_cart_total(cart_items, products)
    
    form = OrderForm()
    
    if form.validate_on_submit():
        order = Order(
            user_id=current_user.id if current_user.is_authenticated else None,
            items=json.dumps([{
                'product_id': item['product'].id,
                'name': item['product'].name,
                'price': item['product'].price,
                'quantity': item['quantity']
            } for item in items_with_products]),
            total_price=total,
            contact_phone=form.contact_phone.data,
            delivery_address=form.delivery_address.data,
            payment_method=form.payment_method.data,
            notes=form.notes.data,
            status='pending'
        )
        
        db.session.add(order)
        
        # Очищаємо кошик
        clear_cart(session)
        
        flash('Замовлення успішно оформлено!', 'success')
        return redirect(url_for('order_confirmation', order_id=order.id))
    
    return render_template('checkout.html',
                         form=form,
                         items=items_with_products,
                         total=total)

@app.route('/order/<int:order_id>')
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order_confirmation.html', order=order)

# Авторизація
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Реєстрація успішна! Тепер ви можете увійти.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Вітаємо у системі!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Невірний email або пароль', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Ви вийшли з системи', 'info')
    return redirect(url_for('index'))

# Профіль користувача
@app.route('/profile')
@login_required
def profile():
    configurations = Configuration.query.filter_by(user_id=current_user.id).order_by(Configuration.created_at.desc()).all()
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    
    return render_template('profile.html',
                         configurations=configurations,
                         orders=orders)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Профіль оновлено', 'success')
        return redirect(url_for('profile'))
    
    return render_template('edit_profile.html', form=form)

# Адмінка
@app.route('/admin')
@admin_required
def admin():
    stats = {
        'users_count': User.query.count(),
        'products_count': Product.query.count(),
        'orders_count': Order.query.count(),
        'total_revenue': sum(o.total_price for o in Order.query.all())
    }
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    return render_template('admin/index.html',
                         stats=stats,
                         recent_orders=recent_orders)

@app.route('/admin/products')
@admin_required
def admin_products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    categories = Category.query.all()
    
    return render_template('admin/products.html',
                         products=products,
                         categories=categories)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            slug=form.slug.data or generate_slug(form.name.data),
            category_id=form.category_id.data,
            price=form.price.data,
            old_price=form.old_price.data,
            brand=form.brand.data,
            stock=form.stock.data,
            description=form.description.data,
            featured=form.featured.data,
            bestseller=form.bestseller.data,
            new=form.new.data
        )
        
        # Обробка завантаження фото
        if form.image.data:
            file = form.image.data
            if file.filename:
                ext = os.path.splitext(file.filename)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png', '.gif']:
                    filename = f"{uuid.uuid4().hex}{ext}"
                    upload_path = os.path.join(app.root_path, 'static', 'images', 'products')
                    os.makedirs(upload_path, exist_ok=True)
                    file.save(os.path.join(upload_path, filename))
                    product.image = f"products/{filename}"
        
        db.session.add(product)
        db.session.commit()
        
        flash('Товар додано', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/product_form.html', form=form, title='Додати товар')

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.slug = form.slug.data or generate_slug(form.name.data)
        product.category_id = form.category_id.data
        product.price = form.price.data
        product.old_price = form.old_price.data
        product.brand = form.brand.data
        product.stock = form.stock.data
        product.description = form.description.data
        product.featured = form.featured.data
        product.bestseller = form.bestseller.data
        product.new = form.new.data
        
        # Обробка завантаження фото
        if form.image.data:
            file = form.image.data
            if file.filename:
                ext = os.path.splitext(file.filename)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png', '.gif']:
                    filename = f"{uuid.uuid4().hex}{ext}"
                    upload_path = os.path.join(app.root_path, 'static', 'images', 'products')
                    os.makedirs(upload_path, exist_ok=True)
                    file.save(os.path.join(upload_path, filename))
                    product.image = f"products/{filename}"
        
        db.session.commit()
        flash('Товар оновлено', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/product_form.html', form=form, title='Редагувати товар')

@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def admin_delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    flash('Товар видалено', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/orders')
@admin_required
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/orders/<int:order_id>')
@admin_required
def admin_order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)

@app.route('/admin/orders/update-status/<int:order_id>', methods=['POST'])
@admin_required
def admin_update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status:
        order.status = new_status
        db.session.commit()
        flash('Статус оновлено', 'success')
    
    return redirect(url_for('admin_order_detail', order_id=order_id))

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/categories')
@admin_required
def admin_categories():
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/add', methods=['GET', 'POST'])
@admin_required
def admin_add_category():
    form = CategoryForm()
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            slug=form.slug.data or generate_slug(form.name.data),
            description=form.description.data,
            icon=form.icon.data
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash('Категорію додано', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/category_form.html', form=form, title='Додати категорію')

@app.route('/admin/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.slug = form.slug.data or generate_slug(form.name.data)
        category.description = form.description.data
        category.icon = form.icon.data
        
        db.session.commit()
        flash('Категорію оновлено', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/category_form.html', form=form, title='Редагувати категорію')

@app.route('/admin/categories/delete/<int:category_id>', methods=['POST'])
@admin_required
def admin_delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    
    flash('Категорію видалено', 'success')
    return redirect(url_for('admin_categories'))

# API для адмінки
@app.route('/admin/api/stats')
@admin_required
def admin_api_stats():
    # Статистика продажів по днях
    orders = Order.query.all()
    
    sales_by_day = {}
    for order in orders:
        day = order.created_at.strftime('%Y-%m-%d')
        if day not in sales_by_day:
            sales_by_day[day] = {'count': 0, 'revenue': 0}
        sales_by_day[day]['count'] += 1
        sales_by_day[day]['revenue'] += order.total_price
    
    return jsonify({
        'sales_by_day': sales_by_day,
        'total_users': User.query.count(),
        'total_products': Product.query.count(),
        'total_orders': Order.query.count(),
        'total_revenue': sum(o.total_price for o in orders)
    })

# Помилки
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
