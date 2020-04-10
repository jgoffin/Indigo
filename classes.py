#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 16:33:39 2020

@author: hannahlyon
"""
from werkzeug.security import check_password_hash, generate_password_hash

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired

from app import db


class User(db.Model):
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

    def change_password(self, old, new):
        if check_password_hash(self.password_hash, old):
            self.set_password(new)
            return 'Password Changed'
        else:
            return 'Invalid Password'

<<<<<<< HEAD
class Files(db.Model, UserMixin):
    
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), nullable=False)
    orig_filename = db.Column(db.String(120), nullable=False)
    file_type = db.Column(db.String(120), nullable=False) # mid or mp3 etc
    model_used = db.Column(db.String(120), nullable=False) # gan, user_upload, rnn, vae, etc
    our_filename =  db.Column(db.String(80), unique=True, nullable=False)
    file_upload_timestamp = db.Column(db.String(120), nullable=False)
    
    def __init__(self, user_name, orig_filename, file_type, model_used,
                 our_filename, file_upload_timestamp):
        self.user_name = user_name
        self.orig_filename = orig_filename
        self.file_type = file_type
        self.model_used = model_used
        self.our_filename = our_filename
        self.file_upload_timestamp = file_upload_timestamp
=======
>>>>>>> 7b0a215b1ebeeca1fd5198c8413d6bcc68164686

class RegistrationForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    email = StringField('Email:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField('Submit')


db.create_all()
db.session.commit()
