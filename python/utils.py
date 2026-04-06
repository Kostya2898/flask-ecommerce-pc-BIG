from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from models import db

def admin_required(f):
    """Декоратор для перевірки прав адміністратора"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Будь ласка, увійдіть в систему', 'warning')
            return redirect(url_for('login'))
        if not current_user.is_admin():
            flash('У вас немає прав для доступу до цієї сторінки', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def get_cart_from_session(session):
    """Отримати кошик з сесії"""
    return session.get('cart', {})

def save_cart_to_session(session, cart):
    """Зберегти кошик в сесію"""
    session['cart'] = cart

def add_to_cart(session, product_id, quantity=1):
    """Додати товар до кошика"""
    cart = get_cart_from_session(session)
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
    else:
        cart[product_id_str] = {'quantity': quantity}
    
    save_cart_to_session(session, cart)
    return cart

def remove_from_cart(session, product_id):
    """Видалити товар з кошика"""
    cart = get_cart_from_session(session)
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
    
    save_cart_to_session(session, cart)
    return cart

def update_cart_quantity(session, product_id, quantity):
    """Оновити кількість товару в кошику"""
    cart = get_cart_from_session(session)
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        if quantity <= 0:
            del cart[product_id_str]
        else:
            cart[product_id_str]['quantity'] = quantity
    
    save_cart_to_session(session, cart)
    return cart

def clear_cart(session):
    """Очистити кошик"""
    save_cart_to_session(session, {})
    return {}

def calculate_cart_total(cart, products):
    """Розрахувати загальну вартість кошика"""
    total = 0
    for product_id, item in cart.items():
        product = next((p for p in products if p.id == int(product_id)), None)
        if product:
            total += product.price * item['quantity']
    return total

def get_cart_items_with_products(cart, products):
    """Отримати список товарів кошика з повними даними"""
    items = []
    for product_id, item in cart.items():
        product = next((p for p in products if p.id == int(product_id)), None)
        if product:
            items.append({
                'product': product,
                'quantity': item['quantity'],
                'subtotal': product.price * item['quantity']
            })
    return items

def check_component_compatibility(components, products_dict):
    """
    Перевірка сумісності компонентів
    components: dict з category_id як ключами і product_id як значеннями
    products_dict: dict з product_id як ключами і product об'єктами як значеннями
    """
    compatibility_issues = []
    
    # Отримуємо компоненти
    cpu = components.get('cpu')
    gpu = components.get('gpu')
    ram = components.get('ram')
    motherboard = components.get('motherboard')
    psu = components.get('psu')
    case = components.get('case')
    storage = components.get('storage')
    
    # Перевірка потужності БЖ
    if psu and gpu:
        psu_product = products_dict.get(psu)
        gpu_product = products_dict.get(gpu)
        
        if psu_product and gpu_product:
            psu_wattage = psu_product.get_specs().get('wattage', 0)
            gpu_tdp = gpu_product.get_specs().get('tdp', 0)
            
            # Додаємо базове споживання (~150W для системи)
            required_wattage = gpu_tdp + 150
            
            if psu_wattage < required_wattage:
                compatibility_issues.append({
                    'type': 'power',
                    'message': f'Блок живлення {psu_wattage}W недостатньо для системи з відеокартою {gpu_tdp}W (потрібно ~{required_wattage}W)'
                })
    
    # Перевірка RAM
    if motherboard and ram:
        mb_product = products_dict.get(motherboard)
        ram_product = products_dict.get(ram)
        
        if mb_product and ram_product:
            mb_ram_type = mb_product.get_specs().get('ram_type', '')
            ram_type = ram_product.get_specs().get('type', '')
            
            if ram_type and mb_ram_type and ram_type != mb_ram_type:
                compatibility_issues.append({
                    'type': 'ram',
                    'message': f'Тип оперативної пам\'яті {ram_type} не сумісний з материнською платою {mb_ram_type}'
                })
    
    # Перевірка сокета CPU і материнської плати
    if cpu and motherboard:
        cpu_product = products_dict.get(cpu)
        mb_product = products_dict.get(motherboard)
        
        if cpu_product and mb_product:
            cpu_socket = cpu_product.get_specs().get('socket', '')
            mb_socket = mb_product.get_specs().get('socket', '')
            
            if cpu_socket and mb_socket and cpu_socket != mb_socket:
                compatibility_issues.append({
                    'type': 'socket',
                    'message': f'Сокет процесора {cpu_socket} не сумісний з материнською платою {mb_socket}'
                })
    
    return {
        'compatible': len(compatibility_issues) == 0,
        'issues': compatibility_issues
    }

def format_price(price):
    """Форматування ціни"""
    return f"{price:,.0f} ₴".replace(',', ' ')

def generate_slug(name):
    """Генерація URL-слага з назви"""
    slug = name.lower()
    slug = slug.replace(' ', '-')
    slug = slug.replace('(', '')
    slug = slug.replace(')', '')
    slug = slug.replace(',', '')
    slug = slug.replace('.', '')
    slug = slug.replace("'", '')
    slug = slug.replace('"', '')
    # Видаляємо всі символи крім букв, цифр та дефісу
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')
    return slug

def create_default_admin():
    """Створення адміністратора за замовчуванням"""
    from models import User
    
    admin = User.query.filter_by(email='admin@igrofix.pc').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@igrofix.pc',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        return True
    return False
