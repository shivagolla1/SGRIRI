from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
# Use SQLite for easier setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rice_mill.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    role = db.Column(db.Enum('admin', 'manager', 'operator'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_id(self):
        return str(self.user_id)

class Broker(db.Model):
    __tablename__ = 'brokers'
    broker_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    commission_rate = db.Column(db.Numeric(5, 2), default=0.00)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Customer(db.Model):
    __tablename__ = 'customers'
    customer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    broker_id = db.Column(db.Integer, db.ForeignKey('brokers.broker_id', ondelete='SET NULL'))
    credit_limit = db.Column(db.Numeric(10, 2), default=0.00)
    current_balance = db.Column(db.Numeric(10, 2), default=0.00)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    broker = db.relationship('Broker', backref='customers')

class RiceType(db.Model):
    __tablename__ = 'rice_types'
    rice_type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    standard_price = db.Column(db.Numeric(10, 2), default=0.00)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PaddyType(db.Model):
    __tablename__ = 'paddy_types'
    paddy_type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    standard_price = db.Column(db.Numeric(10, 2), default=0.00)
    yield_percentage = db.Column(db.Numeric(5, 2), default=0.00)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    supplier_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    contact_person = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    warehouse_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    capacity_bags = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Purchase(db.Model):
    __tablename__ = 'purchases'
    purchase_id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.supplier_id', ondelete='SET NULL'))
    paddy_type_id = db.Column(db.Integer, db.ForeignKey('paddy_types.paddy_type_id'))
    no_of_bags = db.Column(db.Integer, nullable=False)
    price_per_bag = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.warehouse_id', ondelete='SET NULL'))
    purchase_date = db.Column(db.Date, nullable=False)
    delivery_date = db.Column(db.Date)
    payment_status = db.Column(db.Enum('pending', 'partial', 'paid'), default='pending')
    paid_amount = db.Column(db.Numeric(10, 2), default=0.00)
    quality_grade = db.Column(db.Enum('A', 'B', 'C'), default='B')
    moisture_content = db.Column(db.Numeric(5, 2))
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    supplier = db.relationship('Supplier', backref='purchases')
    paddy_type = db.relationship('PaddyType', backref='purchases')
    warehouse = db.relationship('Warehouse', backref='purchases')

class Sale(db.Model):
    __tablename__ = 'sales'
    sale_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'))
    broker_id = db.Column(db.Integer, db.ForeignKey('brokers.broker_id', ondelete='SET NULL'))
    rice_type_id = db.Column(db.Integer, db.ForeignKey('rice_types.rice_type_id'))
    no_of_bags = db.Column(db.Integer, nullable=False)
    price_per_bag = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    sold_date = db.Column(db.Date, nullable=False)
    delivery_date = db.Column(db.Date)
    payment_status = db.Column(db.Enum('pending', 'partial', 'paid'), default='pending')
    paid_amount = db.Column(db.Numeric(10, 2), default=0.00)
    cd_amount = db.Column(db.Numeric(10, 2), default=0.00)
    broker_commission = db.Column(db.Numeric(10, 2), default=0.00)
    delivery_address = db.Column(db.Text)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    customer = db.relationship('Customer', backref='sales')
    broker = db.relationship('Broker', backref='sales')
    rice_type = db.relationship('RiceType', backref='sales')

class RiceStock(db.Model):
    __tablename__ = 'rice_stock'
    stock_id = db.Column(db.Integer, primary_key=True)
    rice_type_id = db.Column(db.Integer, db.ForeignKey('rice_types.rice_type_id'))
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.warehouse_id', ondelete='SET NULL'))
    total_bags = db.Column(db.Integer, default=0)
    reserved_bags = db.Column(db.Integer, default=0)
    available_bags = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    rice_type = db.relationship('RiceType', backref='stock')
    warehouse = db.relationship('Warehouse', backref='rice_stock')

class PaddyStock(db.Model):
    __tablename__ = 'paddy_stock'
    stock_id = db.Column(db.Integer, primary_key=True)
    paddy_type_id = db.Column(db.Integer, db.ForeignKey('paddy_types.paddy_type_id'))
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.warehouse_id', ondelete='SET NULL'))
    total_bags = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    paddy_type = db.relationship('PaddyType', backref='stock')
    warehouse = db.relationship('Warehouse', backref='paddy_stock')

class Payment(db.Model):
    __tablename__ = 'payments'
    payment_id = db.Column(db.Integer, primary_key=True)
    payment_type = db.Column(db.Enum('purchase', 'sale', 'misc', 'broker_commission'), nullable=False)
    related_id = db.Column(db.Integer)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    paid_to = db.Column(db.String(100))
    paid_by = db.Column(db.String(100))
    payment_mode = db.Column(db.Enum('cash', 'cheque', 'bank_transfer', 'upi'), default='cash')
    cheque_number = db.Column(db.String(50))
    bank_name = db.Column(db.String(100))
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Expense(db.Model):
    __tablename__ = 'expenses'
    expense_id = db.Column(db.Integer, primary_key=True)
    expense_category = db.Column(db.Enum('milling', 'transport', 'electricity', 'maintenance', 'salary', 'other'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    expense_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    paid_to = db.Column(db.String(100))
    payment_mode = db.Column(db.Enum('cash', 'cheque', 'bank_transfer'), default='cash')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
@login_required
def dashboard():
    # Dashboard statistics
    total_customers = Customer.query.filter_by(is_active=True).count()
    total_suppliers = Supplier.query.filter_by(is_active=True).count()
    total_brokers = Broker.query.filter_by(is_active=True).count()
    
    # Recent sales
    recent_sales = Sale.query.order_by(Sale.created_at.desc()).limit(5).all()
    
    # Recent purchases
    recent_purchases = Purchase.query.order_by(Purchase.created_at.desc()).limit(5).all()
    
    # Stock summary
    rice_stock = db.session.query(
        RiceType.name,
        db.func.sum(RiceStock.total_bags).label('total_bags'),
        db.func.sum(RiceStock.available_bags).label('available_bags')
    ).join(RiceStock).group_by(RiceType.rice_type_id).all()
    
    return render_template('dashboard.html', 
                         total_customers=total_customers,
                         total_suppliers=total_suppliers,
                         total_brokers=total_brokers,
                         recent_sales=recent_sales,
                         recent_purchases=recent_purchases,
                         rice_stock=rice_stock)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Customer routes
@app.route('/customers')
@login_required
def customers():
    customers_list = Customer.query.all()
    return render_template('customers.html', customers=customers_list)

@app.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        customer = Customer(
            name=request.form['name'],
            phone=request.form['phone'],
            email=request.form['email'],
            address=request.form['address'],
            broker_id=request.form['broker_id'] if request.form['broker_id'] else None,
            credit_limit=request.form['credit_limit'] or 0
        )
        db.session.add(customer)
        db.session.commit()
        flash('Customer added successfully!')
        return redirect(url_for('customers'))
    
    brokers = Broker.query.filter_by(is_active=True).all()
    return render_template('add_customer.html', brokers=brokers)

# Sales routes
@app.route('/sales')
@login_required
def sales():
    sales_list = Sale.query.order_by(Sale.sold_date.desc()).all()
    return render_template('sales.html', sales=sales_list)

@app.route('/sales/add', methods=['GET', 'POST'])
@login_required
def add_sale():
    if request.method == 'POST':
        sale = Sale(
            customer_id=request.form['customer_id'],
            broker_id=request.form['broker_id'] if request.form['broker_id'] else None,
            rice_type_id=request.form['rice_type_id'],
            no_of_bags=int(request.form['no_of_bags']),
            price_per_bag=float(request.form['price_per_bag']),
            total_amount=float(request.form['total_amount']),
            sold_date=datetime.strptime(request.form['sold_date'], '%Y-%m-%d').date(),
            delivery_date=datetime.strptime(request.form['delivery_date'], '%Y-%m-%d').date() if request.form['delivery_date'] else None,
            cd_amount=float(request.form['cd_amount']) if request.form['cd_amount'] else 0,
            broker_commission=float(request.form['broker_commission']) if request.form['broker_commission'] else 0,
            delivery_address=request.form['delivery_address'],
            remarks=request.form['remarks']
        )
        db.session.add(sale)
        db.session.commit()
        flash('Sale added successfully!')
        return redirect(url_for('sales'))
    
    customers = Customer.query.filter_by(is_active=True).all()
    brokers = Broker.query.filter_by(is_active=True).all()
    rice_types = RiceType.query.filter_by(is_active=True).all()
    return render_template('add_sale.html', customers=customers, brokers=brokers, rice_types=rice_types)

# Purchase routes
@app.route('/purchases')
@login_required
def purchases():
    purchases_list = Purchase.query.order_by(Purchase.purchase_date.desc()).all()
    return render_template('purchases.html', purchases=purchases_list)

@app.route('/purchases/add', methods=['GET', 'POST'])
@login_required
def add_purchase():
    if request.method == 'POST':
        purchase = Purchase(
            supplier_id=request.form['supplier_id'],
            paddy_type_id=request.form['paddy_type_id'],
            no_of_bags=int(request.form['no_of_bags']),
            price_per_bag=float(request.form['price_per_bag']),
            total_amount=float(request.form['total_amount']),
            warehouse_id=request.form['warehouse_id'],
            purchase_date=datetime.strptime(request.form['purchase_date'], '%Y-%m-%d').date(),
            delivery_date=datetime.strptime(request.form['delivery_date'], '%Y-%m-%d').date() if request.form['delivery_date'] else None,
            quality_grade=request.form['quality_grade'],
            moisture_content=float(request.form['moisture_content']) if request.form['moisture_content'] else None,
            remarks=request.form['remarks']
        )
        db.session.add(purchase)
        db.session.commit()
        flash('Purchase added successfully!')
        return redirect(url_for('purchases'))
    
    suppliers = Supplier.query.filter_by(is_active=True).all()
    paddy_types = PaddyType.query.filter_by(is_active=True).all()
    warehouses = Warehouse.query.filter_by(is_active=True).all()
    return render_template('add_purchase.html', suppliers=suppliers, paddy_types=paddy_types, warehouses=warehouses)

# Stock routes
@app.route('/stock')
@login_required
def stock():
    rice_stock = db.session.query(
        RiceType.name,
        Warehouse.name.label('warehouse_name'),
        RiceStock.total_bags,
        RiceStock.reserved_bags,
        RiceStock.available_bags
    ).join(RiceStock).join(Warehouse).all()
    
    paddy_stock = db.session.query(
        PaddyType.name,
        Warehouse.name.label('warehouse_name'),
        PaddyStock.total_bags
    ).join(PaddyStock).join(Warehouse).all()
    
    return render_template('stock.html', rice_stock=rice_stock, paddy_stock=paddy_stock)

# Reports routes
@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html')

@app.route('/reports/sales')
@login_required
def sales_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Sale.query
    if start_date:
        query = query.filter(Sale.sold_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Sale.sold_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    sales_data = query.all()
    return render_template('sales_report.html', sales=sales_data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 