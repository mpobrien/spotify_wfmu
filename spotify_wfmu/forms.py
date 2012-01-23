from wtforms import Form, BooleanField, TextField, PasswordField, HiddenField
from wtforms.widgets import TextArea
from wtforms import validators

class LoginForm(Form):
    email = TextField('Email', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])

class RegisterForm(Form):
    name  = TextField('Developer', [validators.Required()])
    email = TextField('Email', [validators.Required(), validators.Email()])
    password = PasswordField('Password', [validators.Required(),
                                          validators.Length(min=6, max=64,message='Password must be at least 6 characters.'),
                                          validators.EqualTo('confirm', message='Passwords must match.')])
    confirm = PasswordField('Confirm Password')
