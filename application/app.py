import os
from flask import Flask, render_template, request, url_for, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import SelectField
from collections import OrderedDict

from sqlalchemy.sql import func

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'jd is crow king'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Clothes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(80), unique=False, nullable=False) # category = top, etc.
    type = db.Column(db.String(80), unique=False, nullable=False) # type = tank top, t shirt, etc.
    color = db.Column(db.String(80), unique=False, nullable=False)
    brand = db.Column(db.String(80), unique=False, nullable=False)
    wears = db.Column(db.Integer)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    def __repr__(self) -> str:
        return "(%s, %s, %s)" % (self.type, self.brand, self.color)


@app.route('/')
def show_all():
   return render_template('show_all.html', clothes = Clothes.query.all())

@app.route('/tops')
def tops():
    return render_template('show_tops.html', clothes = Clothes.query.filter_by(category='top'))


@app.route('/new_item', methods = ['GET', 'POST'])
def new_item():
    if request.method == 'POST':
        if not request.form['category'] or not request.form['type'] or not request.form['brand'] or not request.form['color']:
            flash('Please enter all the fields', 'error')
        else:
            new_item = Clothes(category=request.form['category'],type=request.form['type'],color=request.form['color'],brand=request.form['brand'],wears=0)
            db.session.add(new_item)
            db.session.commit()
            flash('item was successfully added')
            return redirect(url_for('show_all'))
    return render_template('new_item.html')


class enter_wears_form(FlaskForm):
    # val of option, text you see
    category = SelectField('category', choices =[('top'),('bottoms'),('gym'),('outerwear')])
    type = SelectField('type',choices=[])
    brand = SelectField('brand',choices=[])
    color = SelectField('color',choices=[])

def get_distinct_list(myList):
    return list(OrderedDict.fromkeys(myList))

@app.route('/new_wear', methods = ['GET', 'POST'])
def new_wear():
    form = enter_wears_form()
    print([(item.type) for item in Clothes.query.filter_by
                                    (category='top').all()])
    form.type.choices = get_distinct_list([(item.type) for item in Clothes.query.filter_by
                                    (category='top').all()])
    form.brand.choices = get_distinct_list([(item.brand) for item in Clothes.query.filter_by
                                    (category='top',type='tank',).all()])
    form.color.choices = get_distinct_list([(item.color)for item in Clothes.query.filter_by
                                    (category='top',type='tank',brand='brandy').all()])

    if request.method == 'POST':  
        item = Clothes.query.filter_by(category=form.category.data, type=form.type.data, brand=form.brand.data, color=form.color.data).first()
        if item:
            item.wears = item.wears + 1
            db.session.commit()
            return redirect(url_for('show_all'))
        else:
            flash('item does not exist')
    return render_template('new_wear.html',form=form)

@app.route('/type/<category>')
def type(category):
    # gives all the types of a category (types of tops)
    types = Clothes.query.filter_by(category=category).all()
    typeArray = []
    for item in types:
        if item.type not in typeArray:
            typeArray.append(item.type)
    return jsonify({'types' : typeArray})

# type takes in category, brand takes in type and category, color takes in all three
@app.route('/brand/<type>/<category>')
def brand(type, category):
    brands = Clothes.query.filter_by(category=category, type=type).all()
    brandArray = []
    for item in brands:
        if item.brand not in brandArray:
            brandArray.append(item.brand)
    return jsonify({'brands' : brandArray})

@app.route('/color/<brand>/<type>/<category>')
def color(type, category, brand):
    colors =  Clothes.query.filter_by(category=category, type=type, brand=brand).all()
    colorArray = []
    for item in colors:
        if item.color not in colorArray:
            colorArray.append(item.color)
    return jsonify({'colors' : colorArray})
