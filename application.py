import csv
import os
from config import Config
import sys

from config import Config
from flask import render_template, redirect, url_for, request, flash, Flask
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import BooleanField, DateField, IntegerField, SelectField, SubmitField, PasswordField, StringField, validators, Form
from wtforms.validators import DataRequired
from werkzeug.security import check_password_hash, generate_password_hash

import boto3
import time
from io import BytesIO


ALLOWED_EXTENSIONS = {'midi', 'mid'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_s3_obj(bucket_name, output_file):
    """ Read from s3 bucket"""
    try:
        s3 = boto3.resource('s3')
        obj = s3.Object(bucket_name, output_file)
        body = obj.get()['Body'].read().decode('utf-8')
        return body
    except:
        return ""

# Initialization
# Create an application instance (an object of class Flask)  which handles all requests.
application = Flask(__name__)
application.secret_key = os.urandom(24)
application.config.from_object(Config)

db = SQLAlchemy(application)
db.create_all()
db.session.commit()

# login_manager needs to be initiated before running the app
login_manager = LoginManager()
login_manager.init_app(application)

application.config.from_object(Config)

#db = SQLAlchemy(application)
#db.create_all()
#db.session.commit()


class UploadFileForm(FlaskForm):
    """Class for uploading file when submitted"""
    file_selector = FileField('File', validators=[FileRequired()])
    submit = SubmitField('Submit')


class RegistrationForm(FlaskForm):
    """Class for register a new user."""
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])
    submit = SubmitField('Submit')

class LogInForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField('Login')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class FileUpload(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField('Login')

db.create_all()
db.session.commit()


# user_loader :
# This callback is used to reload the user object
# from the user ID stored in the session.
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@application.route('/index')
@application.route('/')
def index():
    """Index Page : Renders index.html with author names."""
    return (render_template('index.html'))


@application.route('/register',  methods=['GET', 'POST'])
def register():
    """
    Register a new user. Save the username, password and email.
    """
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        # user = User(form.username.data, form.email.data,
        #             form.password.data)
        with open('users.csv', mode='w+', newline='') as accounts_file:
            accounts_writer = csv.writer(accounts_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            accounts_writer.writerow([form.username.data, form.email.data, form.password.data])
        # db_session.add(user)
        flash('Thanks for registering')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        username = registration_form.username.data
        password = registration_form.password.data
        email = registration_form.email.data

        user_count = User.query.filter_by(username=username).count() \
                     + User.query.filter_by(email=email).count()
        if (user_count > 0):
            return '<h1>Error - Existing user : ' + username \
                   + ' OR ' + email + '</h1>'
        else:
            user = User(username, email, password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('register.html', form=registration_form)


@application.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LogInForm()
    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        # Look for it in the database.
        user = User.query.filter_by(username=username).first()

        # Login and validate the user.
        if user is not None and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))

    return render_template('login.html', form=login_form)


@application.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@application.route('/upload', methods=['GET', 'POST'])
def upload():
    """upload a file from a client machine."""
    file = UploadFileForm()  # file : UploadFileForm class instance
    if file.validate_on_submit():  # Check if it is a POST request and if it is valid.
        f = file.file_selector.data  # f : Data of FileField
        filename = f.filename
        # filename : filename of FileField
        if not allowed_file(filename):
            flash('Incorrect File Type')
            return redirect(url_for('upload'))

        # save to s3
        #session = boto3.Session(profile_name='msds603')

        # s3 = boto3.resource('s3')
        # s3.Bucket('midi-file-upload').upload_file(filename, 'rushil', filename)
        #s3.Bucket('midi-file-upload').put_object(Key='rushil', Body = request.files['file'])
        
        #conn = S3Connection('AKIAQ3AQGNZZF5QAJBFS','AsVkJF9USDapCzu6ugTLu81Xv+pVvuzfItsUPrtU')
        #bucket = conn.get_bucket('midi-file-upload')
        #file_memory = io.BytesIO(str.encode(f))

        # mem = io.BytesIO()  # transfer stringIO output to Bytes
        # mem.write(proxy.getvalue().encode('utf-8'))
        # mem.seek(0)
        session = boto3.Session(profile_name='msds603')
        # Any clients created from this session will use credentials
        # from the [dev] section of ~/.aws/credentials.
        dev_s3_client = session.resource('s3')

        #s3 = boto3.resource('s3')
        #s3.meta.client.upload_file(file_path, 'midi-file-upload', filename)
        dev_s3_client.meta.client.upload_file(buffer, 'midi-file-upload', filename)

        #self.s3.put_object(Bucket=bucket, Key=key, Body=buffer)

        #file_dir_path = os.path.join(application.instance_path, 'files')
        #file_path = os.path.join(file_dir_path, filename)

        # s3 = boto3.client('s3')
        # #with open(filename, "rb") as rush:
        # s3.upload_file(Key = filename, bucket = "midi-file-upload")
        #f.save(file_path) # Save file to file_path (instance/ + 'files’ + filename)

        #session = boto3.Session(profile_name='msds603')
        # Any clients created from this session will use credentials
        # from the [dev] section of ~/.aws/credentials.
        #dev_s3_client = session.resource('s3')

        #s3 = boto3.resource('s3')
        #s3.meta.client.upload_file(file_path, 'midi-file-upload', filename)
        #dev_s3_client.meta.client.upload_file(file_memory, 'midi-file-upload', filename)

        return('<h1>file uploaded to s3</h1>')
        #return redirect(url_for('index'))  # Redirect to / (/index) page.
    return render_template('upload.html', form=file)


@application.route('/demo', methods=['GET', 'POST'])
def demo():
    """ Load demo page showing Magenta """
    return render_template('demo.html')

@application.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@application.route('/music', methods=['GET', 'POST'])
def music():
    return render_template('music.html')

if __name__ == '__main__':
    application.jinja_env.auto_reload = True
    application.config['TEMPLATES_AUTO_RELOAD'] = True
    application.debug = True
    application.run()
