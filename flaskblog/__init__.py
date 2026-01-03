from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
import os

app = Flask(__name__)

# ---------------- CONFIG ----------------
app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
app.config["SECURITY_PASSWORD_SALT"] = "my_precious_two"

# DB URL (SQLite local / Neon cloud via env)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///site.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ---------------- EXTENSIONS ----------------
db = SQLAlchemy(app)
migrate = Migrate(app, db)   # 🔥 THIS IS THE KEY 🔥
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

mail = Mail(app)

# ---------------- MAIL CONFIG ----------------
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "practicesession3@gmail.com"
app.config["MAIL_PASSWORD"] = "krqc vcmn sqmt kqlv"

# ---------------- ROUTES ----------------
from flaskblog import routes
