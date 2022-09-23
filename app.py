from email import message
import os
from pyexpat.errors import messages
import sys

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(app.root_path, os.getenv('DATABASE_FILE', 'data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
UPLOAD_FOLDER = './static/images_temp'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class User(db.Model, UserMixin):  # 表名将会是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20)) #昵称
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))

    def __init__(self, name, username=None, password=None):
        self.name = name
        self.username = username
        self.password = password

import click
@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    msg=""
    if request.method == 'POST':
        # if 'file' not in request.files:
        #     msg="No file part"
        #     return render_template('index.html', messages=msg)
        
        f = request.files['file']    
        if 'file' not in request.files or f.filename == '':
            msg="No selected file"

        if f:
            # filename = secure_filename(f.filename)
            upload_path = os.path.join(os.path.dirname(__file__), 'static','upload_file_dir', f.filename)
            upload_path = os.path.abspath(upload_path)
            f.save(upload_path)
            msg="successfully"

    return render_template('index.html', messages=msg)

@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@app.route('/do', methods=['GET', 'POST'])
def do():
    return render_template('do.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')

@app.route('/portfolio', methods=['GET', 'POST'])
def portfolio():
    return render_template('portfolio.html')

login_manager = LoginManager(app)
@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg=""
    if request.method == 'POST':
        username_html = request.form['name']
        password_html = request.form['password']

        if not username_html or not password_html:
            msg="none input"

        user = User.query.filter(User.username == username_html).first()
        if username_html == user.username and password_html == user.password:
            login_user(user)
            msg="Login success"
        else:
            msg="Invalid username or password"

    return render_template('login.html',messages=msg)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username_html = request.form['email']
        password_html = request.form['password']
        if username_html and password_html:
            user = User.query.filter(User.username == username_html).first()
            if username_html == user.username and password_html == user.password:
                login_user(user)
                flash('Login success.')
                return redirect(url_for('index'))    
            else:
                flash('Error username or password.')
        else:
            flash('Invalid input.')
            return redirect(url_for('register'))

        register_name_html = request.form['name']
        register_password_html = request.form['password']
        if register_name_html and register_password_html:
            me = User(register_name_html, register_password_html)
            db.session.add(me)
            db.session.commit()
        
        return redirect(url_for('register'))

    return render_template('register.html')

login_manager.login_view = 'login'
# login_manager.login_message = 'Your custom message'


@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)


if __name__ == '__main__':
     app.run(host="0.0.0.0", port=8888, debug = True)