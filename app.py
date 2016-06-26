import base64
import os
import urllib
import requests

from flask import Flask, render_template, request, session, \
					flash, redirect, url_for, g

from flask_bootstrap import Bootstrap

from forms import AuthDBForm

APP_KEY = os.environ['APP_KEY']
APP_SECRET = os.environ['APP_SECRET']

AUTH_REDIRECT_SCHEME='http'

app = Flask(__name__)

bootstrap = Bootstrap(app)

app.config.from_object(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

csrf_token = base64.urlsafe_b64encode(os.urandom(18))

@app.route('/', methods=['GET', 'POST'])
def login():
	session['csrf_token'] = csrf_token
	form = AuthDBForm()
	if form.validate_on_submit():
		return redirect('https://www.dropbox.com/1/oauth2/authorize?%s' % urllib.urlencode({
			'client_id': APP_KEY,
			'redirect_uri': url_for('db_auth_finish', _external=True, _scheme=AUTH_REDIRECT_SCHEME),
			'response_type': 'code',
			'state': csrf_token
			}))
	return render_template('login.html', form=form)

@app.route('/db_auth_finish', methods=['GET', 'POST'])
def db_auth_finish():
	data = requests.post('https://api.dropbox.com/1/oauth2/token',
			data={
				'code': request.args['code'],
				'grant_type': 'authorization_code',
				'redirect_uri': url_for('db_auth_finish', _external=True, _scheme=AUTH_REDIRECT_SCHEME)},
			auth=(APP_KEY, APP_SECRET)).json()
	session['dropbox_user_token'] = data['access_token']
	print data
	return redirect(url_for('main'))

@app.route('/main')
def main():
	return render_template('main.html', data=session['dropbox_user_token'])

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500

if __name__ == '__main__':
	app.run(debug = True)
