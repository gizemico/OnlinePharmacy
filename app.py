from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, ForeignKey, Column,String, Integer,CHAR
from sqlalchemy.ext.declarative import  declarative_base
from sqlalchemy.orm import sessionmaker
import os
from sqlalchemy import insert
from werkzeug.security import check_password_hash


DB_NAME = 'pharmacy.db'

app = Flask(__name__,template_folder="template")
app.config['SECRET_KEY'] = "a"
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
db = SQLAlchemy(app)



class User(db.Model):
	__tablename__ = 'User'
	fullname = db.Column(db.String(50))
	trncid = db.Column(db.String(6), primary_key=True)
	email = db.Column(db.String(100), nullable=False)
	password = db.Column(db.String(4), nullable=False)
	phoneNo = db.Column(db.String(11), nullable=False)
	customer = db.relationship('Customer', backref='Customer')
	doctor = db.relationship('Doctor', backref='Doctor')

class Customer(db.Model):
	__tablename__ = 'Customer'
	customer_id = db.Column(db.String(6), db.ForeignKey('User.trncid'), primary_key=True)
	address = db.Column(db.String(200), nullable=False)
	has1 = db.relationship('Prescription',backref='customer_prescription')
	order = db.relationship('Order', backref='customer_order')

class Doctor(db.Model):
	__tablename__ = 'Doctor'
	doctor_id = db.Column(db.String(6), db.ForeignKey('User.trncid'), primary_key=True)
	gives = db.relationship('Prescription', backref='doctor_prescription')

include=db.Table('include',
				 db.Column('prescriptionID', db.Integer, db.ForeignKey('Prescription.prescriptionID'),nullable=False),
				 db.Column('medicineID',db.Integer, db.ForeignKey('Medicine.medicineID'),nullable=False))

class Prescription(db.Model):
	__tablename__= 'Prescription'
	prescriptionID = db.Column(db.Integer, primary_key=True)
	prescriptionExpirationDate = db.Column(db.String(50),nullable=False)
	prescription_customer_id = db.Column(db.String(6), db.ForeignKey('Customer.customer_id'))
	prescription_doctor_id = db.Column(db.String(6), db.ForeignKey('Doctor.doctor_id'))
	Medicines = db.relationship('Medicine',secondary=include,backref='medicine_prescription')
	owns_p = db.relationship('Order',backref='prescription_order', uselist=False)


class Medicine(db.Model):
	__tablename__= 'Medicine'
	medicineID = db.Column(db.Integer, primary_key=True)
	medicineDetail = db.Column(db.String(200), nullable=False)
	medicineName = db.Column(db.String(50), nullable=False)
	medicineType = db.Column(db.String(50), nullable=False)
	Prescriptions = db.relationship('Prescription',secondary=include,backref='medicine_prescription')
	contains = db.relationship('Stock', backref='medicine_stock')

class Stock(db.Model):
	__tablename__= 'Stock'
	barcode = db.Column(db.Integer, primary_key=True)
	stockID = db.Column(db.Integer, nullable=False)
	price = db.Column(db.Integer, nullable=False)
	brand = db.Column(db.String(50), nullable=False)
	description = db.Column(db.String(100), nullable=False)
	category = db.Column(db.String(100), nullable=False)
	stockExpirationDate = db.Column(db.String(50), nullable=False)
	Stock_medicineID = db.Column(db.Integer, db.ForeignKey("Medicine.medicineID"))
	Stock_pharmacyName = db.Column(db.String(100),db.ForeignKey("Pharmacy.pharmacyName"))
	Stock_orderID = db.Column(db.Integer, db.ForeignKey("Order.orderID"))

class Pharmacy(db.Model):
	__tablename__= 'Pharmacy'
	pharmacyName = db.Column(db.String(100), primary_key=True)
	location = db.Column(db.String(50), nullable=False)
	website = db.Column(db.String(100), nullable=False)
	contactNo = db.Column(db.String(13), nullable=False)
	has2 = db.relationship('Stock', backref='pharmacy_stock')

class Order(db.Model):
	__tablename__= 'Order'
	orderID = db.Column(db.Integer, primary_key=True)
	quantity = db.Column(db.Integer, nullable=False)
	rate = db.Column(db.Integer, nullable=False)
	comment = db.Column(db.String(100))
	orderDate = db.Column(db.String(50), nullable=False)
	deliveryStatus = db.Column(db.String(20), nullable=False)
	totalCost = db.Column(db.Integer, nullable=False)
	consist = db.relationship('Stock', backref='order_stock')
	owns_o = db.Column(db.Integer, db.ForeignKey('Prescription.prescriptionID'), unique=True)
	order_customer = db.Column(db.String(6), db.ForeignKey('Customer.customer_id'))



#home page is created for user selection buttons
@app.route("/", methods=["GET", "POST"])
def home():
	if request.method == 'POST':
		if request.form.get('action1') == 'Customer Login':
			return redirect(url_for('clogin'))

		elif request.form.get('action2') == 'Doctor Login':
			return redirect(url_for('login'))

		elif request.form.get('action3') == 'Customer Register':
			return redirect(url_for('cregister'))

		elif request.form.get('action4') == 'Doctor Register':
			return redirect(url_for('register'))

	return render_template("home.html")

#doctor register page
@app.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "POST":
		fullname =request.form.get("name")
		trncid = request.form.get("trncid")
		email = request.form.get("email")
		password = request.form.get("password")
		phoneNo = request.form.get("phoneNo")

		search = User.query.filter_by(trncid=trncid).first()

		if search != None:
			flash("An account with this TRNCID already exists.")
			return render_template('register.html')

		new_user = User(fullname=fullname, trncid=trncid,
						email=email, password=password, phoneNo=phoneNo)
		new_doctor = Doctor(doctor_id=trncid)

		db.session.add(new_user)
		db.session.commit()

		db.session.add(new_doctor)
		db.session.commit()

		return redirect(url_for('login'))

	return render_template("register.html")

#customer register page
@app.route("/cregister", methods=["GET", "POST"])
def cregister():
	if request.method == "POST":
		fullname =request.form.get("name")
		trncid = request.form.get("trncid")
		email = request.form.get("email")
		password = request.form.get("password")
		phoneNo = request.form.get("phoneNo")
		address = request.form.get("address")

		search = User.query.filter_by(trncid=trncid).first()

		if search != None:
			flash("An account with this TRNCID already exists.")
			return render_template('cregister.html')

		new_user = User(fullname=fullname, trncid=trncid, email=email,
						password=password, phoneNo=phoneNo)

		new_customer = Customer(customer_id=trncid, address=address)

		db.session.add(new_user)
		db.session.commit()

		db.session.add(new_customer)
		db.session.commit()

		return redirect(url_for('login'))

	return render_template("cregister.html")

#doctor Login page
@app.route("/login", methods=["GET","POST"])
def login():
	if request.method == "POST":
		trncid = request.form.get("trncid")
		password = request.form.get("password")

		search = User.query.filter_by(trncid=trncid).first()

		if search is None:
			flash('Try again with correct TRNCID!')
			return render_template('login.html')

		if password == search.password:
			return redirect(url_for('prescription'))
	return render_template("login.html")

#customer Login page
@app.route("/clogin", methods=["GET","POST"])
def clogin():
	if request.method == "POST":
		trncid = request.form.get("trncid")
		password = request.form.get("password")

		search = User.query.filter_by(trncid=trncid).first()

		if search is None:
			flash("Try again with correct TRNCID!")
			return render_template('clogin.html')

		if password == search.password:
			return redirect(url_for('order'))
	return render_template("clogin.html")

#doctor write prescription into prescription page
@app.route("/prescription", methods=["GET","POST"])
def prescription():
	if request.method == "POST":
		prescriptionID = request.form.get("prescriptionID")
		prescriptionExpirationDate = request.form.get("prescriptionExpirationDate")
		medicineID =request.form.get("medicineID")
		#trncid = request.form.get("trncid")
		trncid = request.form.get("trncid")

		new_prescription = Prescription(prescriptionID=prescriptionID,prescriptionExpirationDate=prescriptionExpirationDate, prescription_customer_id=trncid)

		db.session.add(new_prescription)
		db.session.commit()

	return render_template("prescription.html")

#customer gives order into order page page
@app.route("/order", methods=["GET","POST"])
def order():
	if request.method == "POST":
		orderID = request.form.get("orderID")
		quantity = request.form.get("quantity")
		rate =request.form.get("rate")
		comment = request.form.get("comment")
		orderDate = request.form.get("orderDate")
		deliveryStatus =request.form.get("deliveryStatus")
		totalCost = quantity*2
		owns_o = request.form.get("owns_o")

		new_order = Order(orderID=orderID,quantity=quantity,rate=rate,comment=comment,
						orderDate=orderDate,deliveryStatus=deliveryStatus,totalCost=totalCost, owns_o=owns_o)

		db.session.add(new_order)
		db.session.commit()

	return render_template("order.html")


@app.errorhandler(404)
def error(e):
	return render_template("404.html")


if __name__=="__main__":

	if not os.path.exists(DB_NAME):
		with app.app_context():
			db.create_all()

	app.debug=True
	app.run()