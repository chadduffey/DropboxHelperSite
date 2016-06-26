from flask_wtf import Form

from wtforms import SubmitField

class AuthDBForm(Form):
	submit = SubmitField('Log in to your Dropbox account')