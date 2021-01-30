from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError
from emis_app.models import Emis_users
from os import environ

class LoginForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    submit = SubmitField('Login')

class AddUserForm(FlaskForm):
    admin_key = PasswordField('Admin Key', validators = [DataRequired()])
    username = StringField('Username', validators = [DataRequired()])
    fullname = StringField('Full Name', validators = [DataRequired()])
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
        validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField('Add User')
    
    def validate_username(self, username):
        user = Emis_users.query.filter(Emis_users.username == username.data).first()
        if user:
            raise ValidationError('username already exists.')
    
    def validate_admin_key(self, admin_key):
        if admin_key.data != environ.get('ADMIN_KEY'):
            raise ValidationError('Invalid Admin Key.')
    