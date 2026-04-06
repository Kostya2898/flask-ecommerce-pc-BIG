from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FloatField, IntegerField, SelectField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange, ValidationError
from models import User, Category

class RegistrationForm(FlaskForm):
    """Форма реєстрації користувача"""
    username = StringField("Ім'я користувача", validators=[
        DataRequired(message="Введіть ім'я користувача"),
        Length(min=3, max=80, message="Ім'я має бути від 3 до 80 символів")
    ])
    email = StringField("Електронна пошта", validators=[
        DataRequired(message="Введіть email"),
        Email(message="Невірний формат email")
    ])
    password = PasswordField("Пароль", validators=[
        DataRequired(message="Введіть пароль"),
        Length(min=6, message="Пароль має бути щонайменше 6 символів")
    ])
    confirm_password = PasswordField("Підтвердження пароля", validators=[
        DataRequired(message="Підтвердіть пароль"),
        EqualTo('password', message="Паролі не співпадають")
    ])
    submit = SubmitField("Зареєструватися")
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Це ім'я користувача вже зайняте")
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Цей email вже зареєстрований")

class LoginForm(FlaskForm):
    """Форма входу"""
    email = StringField("Електронна пошта", validators=[
        DataRequired(message="Введіть email"),
        Email(message="Невірний формат email")
    ])
    password = PasswordField("Пароль", validators=[
        DataRequired(message="Введіть пароль")
    ])
    remember = BooleanField("Запам'ятати мене")
    submit = SubmitField("Увійти")

class ProfileForm(FlaskForm):
    """Форма редагування профілю"""
    username = StringField("Ім'я користувача", validators=[
        DataRequired(message="Введіть ім'я користувача"),
        Length(min=3, max=80, message="Ім'я має бути від 3 до 80 символів")
    ])
    email = StringField("Електронна пошта", validators=[
        DataRequired(message="Введіть email"),
        Email(message="Невірний формат email")
    ])
    phone = StringField("Телефон", validators=[
        Optional()
    ])
    address = TextAreaField("Адреса доставки", validators=[
        Optional()
    ])
    submit = SubmitField("Зберегти зміни")

class CategoryForm(FlaskForm):
    """Форма категорії"""
    name = StringField("Назва категорії", validators=[
        DataRequired(message="Введіть назву категорії"),
        Length(max=100, message="Назва занадто довга")
    ])
    slug = StringField("URL-слаг", validators=[
        DataRequired(message="Введіть URL-слаг"),
        Length(max=100, message="Слаг занадто довгий")
    ])
    description = TextAreaField("Опис")
    icon = SelectField("Іконка", choices=[
        ('cpu', 'Процесор (CPU)'),
        ('gpu', 'Відеокарта (GPU)'),
        ('ram', 'Оперативна пам\'ять (RAM)'),
        ('storage', 'Накопичувач (SSD/HDD)'),
        ('psu', 'Блок живлення (PSU)'),
        ('case', 'Корпус'),
        ('motherboard', 'Материнська плата'),
        ('cooling', 'Система охолодження')
    ])
    submit = SubmitField("Зберегти")

class ProductForm(FlaskForm):
    """Форма товару"""
    name = StringField("Назва товару", validators=[
        DataRequired(message="Введіть назву товару"),
        Length(max=200, message="Назва занадто довга")
    ])
    slug = StringField("URL-слаг", validators=[
        DataRequired(message="Введіть URL-слаг"),
        Length(max=200, message="Слаг занадто довгий")
    ])
    category_id = SelectField("Категорії", coerce=int, validators=[
        DataRequired(message="Оберіть категорію")
    ])
    price = FloatField("Ціна", validators=[
        DataRequired(message="Введіть ціну"),
        NumberRange(min=0, message="Ціна не може бути від'ємною")
    ])
    old_price = FloatField("Стара ціна", validators=[
        Optional(),
        NumberRange(min=0, message="Ціна не може бути від'ємною")
    ])
    brand = StringField("Бренд", validators=[
        Optional()
    ])
    stock = IntegerField("Кількість на складі", validators=[
        DataRequired(message="Введіть кількість"),
        NumberRange(min=0, message="Кількість не може бути від'ємною")
    ])
    description = TextAreaField("Опис")
    featured = BooleanField("Рекомендований товар")
    bestseller = BooleanField("Бестселер")
    new = BooleanField("Новинка")
    image = FileField("Фото товару")
    submit = SubmitField("Зберегти")

class OrderForm(FlaskForm):
    """Форма оформлення замовлення"""
    contact_phone = StringField("Телефон для зв'язку", validators=[
        DataRequired(message="Введіть номер телефону"),
        Length(min=10, max=20, message="Невірний номер телефону")
    ])
    delivery_address = TextAreaField("Адреса доставки", validators=[
        DataRequired(message="Введіть адресу доставки")
    ])
    payment_method = SelectField("Спосіб оплати", choices=[
        ('card', 'Оплата картою онлайн'),
        ('cash', 'Оплата готівкою при отриманні'),
        ('installment', 'Розстрочка')
    ])
    notes = TextAreaField("Коментар до замовлення", validators=[
        Optional()
    ])
    submit = SubmitField("Оформити замовлення")

class ConfigurationForm(FlaskForm):
    """Форма збереження конфігурації"""
    name = StringField("Назва конфігурації", validators=[
        DataRequired(message="Введіть назву конфігурації"),
        Length(max=100, message="Назва занадто довга")
    ])
    submit = SubmitField("Зберегти конфігурацію")
