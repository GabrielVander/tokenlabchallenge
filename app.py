from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from util import randomString, print_to_console
from datetime import datetime, timedelta
import os
from os.path import join, dirname, realpath

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = randomString()
app.config["UPLOAD_FOLDER"] = join(dirname(realpath(__file__)), r"static\images\uploads")

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import *

@app.route('/')
def index():
    try:
        user_id = session['user_id']

        user = User.query.filter_by(id=user_id).first()

        events = Event.query.all()

        return redirect(url_for('upcomming'))

    except:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()

        if user is not None and user.check_password(request.form['pass']):
            session['user_id'] = user.id
            return redirect(url_for('index'))
            
        else:
            flash('Incorrect username/password')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':

        if User.query.filter_by(email=request.form['email']).first() is not None:
            flash('Email already registered')
            return redirect(url_for('signup'))

        if User.query.filter_by(username=request.form['username']).first() is not None:
            flash('Username already registered')
            return redirect(url_for('signup'))

        user = User(request.form['email'],
                    request.form['username'], request.form['pass'])

        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id

        return redirect(url_for('index'))

    return render_template('signup.html')


@app.route('/leave')
def leave():
    session.clear()

    return redirect(url_for('index'))


@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    try:
        user_id = session['user_id']

    except:
        return redirect(url_for('index'))

    user = User.query.filter_by(id=user_id).first()

    if request.method == 'POST':
        start = datetime.now().strftime('%d/%m/%Y %H:%M') if not request.form['date-start'] else request.form['date-start']
        try:
            end = start if not request.form['date-finish'] else request.form['date-finish']

        except(KeyError):
            end = start

        start_date = datetime.strptime(
            start, '%d/%m/%Y %H:%M')

        finish_date = datetime.strptime(
            end, '%d/%m/%Y %H:%M')

        event = Event(request.form['title'], request.form['description'],
                        start_date, finish_date, user.username)

        user.attending.append(event)

        attendees = request.form['attendees'].split(';')

        for i in attendees:
            if not i:
                pass

            us = User.query.filter_by(username=i).first()

            if us and us not in event.attendees:
                us.attending.append(event)

        current_db_sessions = db.object_session(event)
        current_db_sessions.add(event)
        db.session.commit()

        return redirect(url_for('upcomming'))

    else:
        events = Event.query.filter(Event.attendees.contains(user)).all()

        disabled_dates = []

        for i in events:
            date_range = [
                i.starts_at + timedelta(days=x) for x in range(0, (i.ends_at-i.starts_at).days)]

            disabled_dates.extend(date_range)

        var = [x.strftime('%d/%m/%Y %H:%M').split(' ')[0]
                for x in disabled_dates]

        return render_template('add_event.html', user=user, disabled_dates=var)
    

@app.route('/upcomming')
def upcomming():
    try:
        user_id = session['user_id']

    except:
        return redirect(url_for('index'))

    user = User.query.filter_by(id=user_id).first()

    events = Event.query.filter(
        Event.attendees.contains(user)).order_by(Event.ends_at)

    return render_template('upcomming.html', user=user, events=events, now=datetime.now, event=None)


@app.route('/exclude/<int:id>')
def exclude(id):
    try:
        user_id = session['user_id']

        event = Event.query.filter_by(id=id).first()

        user = User.query.filter_by(id=user_id).first()

        user.attending.remove(event)

        db.session.commit()

    except:
        pass

    finally:
        return redirect(url_for('index'))


@app.route('/edit_event/<int:id>', methods=['GET', 'POST'])
def edit_event(id):
    try:
        user_id = session['user_id']

    except:
        return redirect(url_for('index'))

    event = Event.query.filter_by(id=id).first()


    user = User.query.filter_by(id=user_id).first()

    if request.method == 'POST':

        event.title = request.form['title']
        event.description = request.form['description']

        attendees = request.form['attendees'].split(';')
        for i in attendees:
            if not i:
                pass

            us = User.query.filter_by(username=i).first()

            if us and us not in event.attendees:
                us.attending.append(event)

        db.session.commit()

        return redirect(url_for('index'))

    else:
        return render_template('add_event.html', user=user, event=event, 
                                map=map, str=str, disabled_dates=[])
    

@app.route('/profile_pic', methods=['GET', 'POST'])
def profile_pic():
    try:
        user_id = session['user_id']

        user = User.query.filter_by(id=user_id).first()
        if request.method == "POST":
        
            if request.files:

                image = request.files["image"]

                image.save(os.path.join(app.config["UPLOAD_FOLDER"], image.filename))
                user.profile_image = '../static/images/uploads/' + image.filename

                db.session.commit()
    except:
        pass

    finally:
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
