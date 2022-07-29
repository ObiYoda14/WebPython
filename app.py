# Primeira letra maiúscula Classe e tudo minusculo é função
from flask import Flask, render_template, redirect, url_for, request, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
# Plugin de Flask Login (pip install flask-login)
# UserMixin é tipo um db.Model
from flask_login import LoginManager, UserMixin, current_user, logout_user, login_user
#Módulo de Segurança instalado junto com o Flask para criptrografia da senhas
from werkzeug.security import check_password_hash, generate_password_hash

from sqlalchemy.exc import IntegrityError

# Atribui o Flask para a variável app ("hello" é o nome do app mas não usa pra nada)
app = Flask("hello")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#Chave de criptografia para encriptar os dados
app.config["SECRET_KEY"] = "pudim"

# Cria a varíavel referente ao Banco de Dados
db = SQLAlchemy(app)
# Cria a varíavel refernte ao login
login = LoginManager(app)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(70), nullable=False)
    body = db.Column(db.String(500))
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True, index=True)
    email =  db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    posts = db.relationship('Post', backref='author')

    # Converte o password no formato hash
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Compara o password digitado com o password armazenado no banco
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Fazer query no DB para buscar o usuário
# "@" é um decorator que serve para modificar um função que está abaixo
@login.user_loader 
def load_user(id):
    # Busca o ID do usuário no DB convertendo a string para inteiro (no DB o campo ID é Integer)
    return User.query.get(int(id))

# Função para criar as tabelas no banco, se já existe, ele não cria
db.create_all()

@app.route("/")
def index():
    posts = Post.query.all()
    return render_template("index.html", posts=posts)

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        try:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            flash("Username or E-mail already exists!")
        else:
            return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash("Incorrect Username or Password")
            return redirect(url_for("login"))
        login_user(user)
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

#@app.route("/populate")
#def populate():
#    user = User(username='Herman', email="email@email.com", password_rash="a")
#    post1 = Post(title="Post 1", body="Texto do post 1", author=user)
#    post2 = Post(title="Post 2", body="Texto do post 2", author=user)
#    db.session.add(user)
#    # A session garante que só será gravado se todas os registros forem inseridos sem erro
#    db.session.add(post1)
#    db.session.add(post2)
#    db.session.commit()
#    return redirect(url_for('index'))