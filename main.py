from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.automap import automap_base
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FloatField
from wtforms.validators import DataRequired, URL, NumberRange
from flask_bootstrap import Bootstrap5

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
db.init_app(app)

Base = automap_base()


class AddCafe(FlaskForm):
    name = StringField('Cafe Name', validators=[DataRequired()])
    location = StringField('Cafe city', validators=[DataRequired()])
    map_url = StringField('Map Url', validators=[DataRequired(), URL()])
    img_url = StringField('Image Url', validators=[DataRequired(), URL()])
    sockets = SelectField('Sockets', choices=[(0, 'no'), (1, 'yes')])
    wifi = SelectField('Wifi', choices=[(0, 'no'), (1, 'yes')])
    toilet = SelectField('Restroom availability', choices=[(0, 'no'), (1, 'yes')])
    calls = SelectField('Can have calls', choices=[(0, 'no'), (1, 'yes')])
    seats = SelectField('Seats', choices=['0-10', '10-20', '20-30', '30-40', '40-50', '50+'],
                        validators=[DataRequired()])
    price = FloatField('Coffee price in GBP', validators=[DataRequired(), NumberRange(min=0, max=100)])
    submit = SubmitField('Submit')


@app.route('/')
def home():
    result = db.session.query(Cafe).all()
    return render_template('index_2.html', cafes=result[0:9], previous='disabled', page_num=1)


@app.route('/pages/<int:num>')
def pages(num):

    if num == 1:
        previous = 'disabled'
    else:
        previous = ''
    result = db.session.query(Cafe).all()
    cafes = [0, result[0:9], result[9:18], result[18:]]
    return render_template('index_2.html', cafes=cafes[num], previous=previous, page_num=num)


@app.route('/cafe/<int:cafe_id>')
def cafe(cafe_id):
    res_cafe = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
    print(res_cafe.name)
    return render_template('cafe.html', cafe=res_cafe)


@app.route('/add', methods=['POST', 'GET'])
def add():
    form = AddCafe()
    if request.method == 'POST' and form.validate_on_submit():
        new_cafe = Cafe(name=form.name.data, map_url=form.map_url.data, img_url=form.img_url.data,
                        location=form.location.data,has_sockets=int(form.sockets.data),
                        has_toilet=int(form.toilet.data), has_wifi=int(form.wifi.data),
                        can_take_calls=int(form.calls.data), seats=form.seats.data, coffee_price=f'£{form.price.data}')
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('home'))
    elif request.method == 'GET':
        return render_template('add_cafe.html', form=form)
    else:
        return render_template('error.html')



if __name__ == '__main__':
    with app.app_context():
        Base.prepare(db.engine, reflect=True)
        Cafe = Base.classes.cafe
    app.run(debug=True)
