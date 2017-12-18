from flask import (Flask, g, render_template, flash, redirect, url_for)
from flask_login import (LoginManager, login_user, logout_user, login_required,
                         current_user)
from flask_bcrypt import check_password_hash

import server.forms as forms
import server.models as models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'sdrldskfj.lsdifjdslk.34.slkfjdslkjf.adkfj!'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None

@app.before_request
def before_request():
    """connect to teh database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user

@app.after_request
def after_request(response):
    """close the database connection after each request."""
    g.db.close()
    return response

@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("You registered for the greatest app in the world", "success")
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!", "error")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out", "success")
    return redirect(url_for('login'))


@app.route('/new_post', methods=('GET', 'POST'))
@login_required
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        models.Post.create(user=g.user._get_current_object(),
                           content=form.content.data.strip())
        flash("Message posted! Thanks!", "success")
        return redirect(url_for('index'))
    return render_template('post.html', form=form)

@app.route('/')
def index():
    return 'hey'

if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='jordancasoli',
            email='casolijordan@gmail.com',
            password='password',
            admin=True
        )
    except:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)