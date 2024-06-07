from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///warehouse.db'
db = SQLAlchemy(app)

class Warehouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Balance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

@app.before_request
def initialize_balance():
    balance = Balance.query.first()
    if not balance:
        initial_balance = Balance(amount=10000)
        db.session.add(initial_balance)
        db.session.commit()


@app.route('/')
def index():
    warehouse_list = Warehouse.query.all()
    account = Balance.query.first().amount
    return render_template("index.html", warehouse=warehouse_list, balance=account)


@app.route('/history')
def history():
    operations_recorded = History.query.all()
    account = Balance.query.first().amount
    return render_template("history.html", operations_recorded=operations_recorded, balance=account)

@app.route('/history/<history_id>', methods=['GET','POST'])
def delete_history(history_id):
    delete = History.query.filter_by(id=history_id).first()
    db.session.delete(delete)
    db.session.commit()

    operations_recorded = History.query.all()
    account = Balance.query.first().amount

    return render_template("history.html", operations_recorded=operations_recorded, balance=account)


@app.route('/purchase')
def purchase():
    account = Balance.query.first().amount
    return render_template('purchase.html', balance=account)

@app.route('/submit_purchase', methods=['POST'])
def submit_purchase():
    balance_record = Balance.query.first()
    account = balance_record.amount
    warehouse_list = Warehouse.query.all()

    name = request.form['name']
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])

    if account >= price * quantity:
    # If user enters the same item, this will catch it and it will add the quantity, if not it will add the dict to the list warehouse_list[] 
        item_exist = False

        for p in warehouse_list:
            if p.name == name:
                p.quantity += quantity
                item_exist = True
                break

        if not item_exist:
            new_purchase = Warehouse(name=name, price=price, quantity=quantity)
            db.session.add(new_purchase)

        
        account -= price * quantity # substract the purchased items from the account
        balance_record.amount = account
        db.session.commit()

        new_purchase_history = History(type='purchase action', name=name, price=price, quantity=quantity)
        db.session.add(new_purchase_history)
        db.session.commit()

        # success_message = f"Purchase has been successful! {quantity} unit(s) of {name} bought for a total of {price * quantity}."
        # time.sleep(2)
        # return render_template('purchase.html', balance=account, success_message=success_message)

    else:
        error_message_funds = "You're broke Bruah! Retry when you've got Coins! ;)"
        return render_template('purchase.html', balance=account, error_message_funds=error_message_funds)


    # Redirect me to the main page
    return redirect('/') 


@app.route('/sale')
def sale():
    account = Balance.query.first().amount
    return render_template("sale.html", balance=account)

@app.route('/submit_sale', methods=['POST'])
def submit_sale():
    balance_record = Balance.query.first()
    account = balance_record.amount
    warehouse_list = Warehouse.query.all()

    name = request.form['name']
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])

    product_found = False  # Flag to check if the product exists in the database

    for s in warehouse_list:
        if s.name == name:
            product_found = True
            if s.quantity < quantity:
                # Insufficient quantity, do not process the sale
                error_message = f"Insufficient quantity for {name}. Available: {s.quantity}, Requested: {quantity}"
                return render_template('sale.html', balance=account, error_message=error_message)
            else:
                # Process the sale
                s.quantity -= quantity
                account += price * quantity
                if s.quantity <= 0:
                    db.session.delete(s)
                balance_record.amount = account
                db.session.commit()

                new_sale_history = History(type='sale action', name=name, price=price, quantity=quantity)
                db.session.add(new_sale_history)
                db.session.commit()
                    
                break
    if not product_found:
        # If the product is not found in the database
        error_message_name = f"Product '{name}' not found in the database."
        return render_template('sale.html', balance=account, error_message_name=error_message_name)

    # Redirect me to the main page
    return redirect('/') 

@app.route('/balance')
def balance():
    account = Balance.query.first().amount
    return render_template("balance.html", balance=account)

@app.route('/submit_balance', methods=['POST'])
def submit_balance():
    balance_record = Balance.query.first()
    account = balance_record.amount
    amount = float(request.form['money']) # 'money' is the name found in the balance.html
    operation = request.form['balance'] # 'balance' is the name found in the balance.html

    if operation == 'Add':
        account += amount
        add_money = History(type='Balance ADD action', name='Add', price=amount, quantity='N/A')
        db.session.add(add_money)
        db.session.commit()
    elif operation == 'Withdraw' and account >= amount:
        account -= amount
        withdraw_money = History(type='Balance WITHDRAW action', name='Withdraw', price=amount, quantity='N/A')
        db.session.add(withdraw_money)
        db.session.commit()
    else:
        error_message_funds_again = "I do it for you, Trust me Bro!"
        return render_template("balance.html", balance=account, error_message_funds_again=error_message_funds_again)


    balance_record.amount = account
    db.session.commit()
    
    # Redirect me to the main page
    return redirect('/') 


with app.app_context():
    db.create_all()

app.run(debug=True)