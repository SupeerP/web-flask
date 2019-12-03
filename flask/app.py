from flask import Flask, request, url_for, render_template, flash, redirect, session
from forms import RegistrationForm, LoginForm
from pickleshare import PickleShareDB
from pymongo import MongoClient

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretkey'

posts = [
    {
        'author' : 'Pedro Parrilla',
        'title' : 'Sample Title',
        'content' : 'Sample post content',
        'date_posted' : '3 Abril' 
    },
]

client = MongoClient("mongo", 27017)
db = client.SampleCollections

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' in session:
        return render_template('home.html', login = 'username', posts = posts)
    return render_template('home.html', posts = posts)

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        db = PickleShareDB('miBD')
        try:
            if db.keys().index(f'{form.username.data}') != ValueError:
                flash('User already exist', 'danger')
            else:
                raise ValueError
        except ValueError:
            flash(f'Account created for {form.username.data}!', 'success')
            db[f'{form.username.data}'] = { 'pass' : f'{form.password.data}' }
            return redirect(url_for('home'))
    return render_template('register.html', title='Register', form = form)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db = PickleShareDB('miBD')
        try:
            if db.keys().index(f'{form.username.data}') != ValueError and form.password.data == db[f'{form.username.data}']['pass']:
                flash(f'Hi {form.username.data}!', 'success')
                session['username'] = f'{form.username.data}'
                return redirect(url_for('home'))
            else:
                raise ValueError
        except ValueError:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form = form)

@app.route('/logout')
def logout():
    session.clear()
    flash(f'See you!', 'success')
    return redirect(url_for('home'))


@app.route('/movies', methods=['GET','POST'])
def movies():
    movies = db.video_movies.find()
    if 'username' in session:
        data = request.form.get('title')
        if data is not None:

            if request.form.get('action') == 'add':
                movie = { "title" : data,
                        "year" : request.form.get('year'),
                        "imdb" : request.form.get('imdb')}
                duplicate = db.video_movies.find_one({"title" : data})
                if duplicate is None:
                    db.video_movies.insert_one(movie)
                    flash(f'Added \'{data}\'', 'success')
                else:
                    flash(f'\'{data}\' already exists', 'danger')

            elif request.form.get('action') == 'delete':
                exist = db.video_movies.find_one({"title" : data})
                if exist is not None:
                    db.video_movies.delete_one(exist)
                    flash(f'Deleted \'{data}\'', 'success')
                else:
                    flash(f'\'{data}\' doesn\'t exist', 'danger')

            else:
                exist = db.video_movies.find_one({"title" : data})
                n_title = request.form.get('n_title')
                if exist is None:
                    flash(f'\'{data}\' doesn\'t exist', 'danger')
                elif n_title is "" :
                    flash(f'Insert a Title', 'danger')
                else:
                    movie = { "title" : n_title,
                        "year" : request.form.get('n_year'),
                        "imdb" : request.form.get('n_imdb')}
                    db.video_movies.delete_one(exist)
                    db.video_movies.insert_one(movie)
                    flash(f'Modify to \'{ n_title }\'', 'success')
                    

        return render_template('movies.html', movies = movies, login = 'username')
    return render_template('movies.html', movies = movies)

@app.errorhandler(404)
def page_not_found(error):
    return 'La página no existe'
