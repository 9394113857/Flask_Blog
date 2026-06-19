from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate

from dotenv import load_dotenv
import os

# =====================================================
# LOAD ENVIRONMENT VARIABLES
# =====================================================

load_dotenv()

# =====================================================
# CREATE FLASK APPLICATION
# =====================================================

app = Flask(__name__)

# =====================================================
# SECURITY CONFIGURATION
# =====================================================

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

app.config["SECURITY_PASSWORD_SALT"] = os.getenv(
    "SECURITY_PASSWORD_SALT",
    "my_precious_two"
)

# =====================================================
# DATABASE CONFIGURATION
# CURRENT:
# SQLite Local Database
#
# FUTURE:
# Neon PostgreSQL
#
# Only .env changes needed later
# =====================================================

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///site.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# =====================================================
# MAIL CONFIGURATION
# =====================================================

app.config["MAIL_SERVER"] = "smtp.gmail.com"

app.config["MAIL_PORT"] = 587

app.config["MAIL_USE_TLS"] = True

app.config["MAIL_USE_SSL"] = False

app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")

app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

app.config["MAIL_DEFAULT_SENDER"] = os.getenv(
    "MAIL_USERNAME"
)

# =====================================================
# DATABASE OBJECT
# =====================================================

db = SQLAlchemy(app)

# =====================================================
# DATABASE MIGRATIONS
# =====================================================

migrate = Migrate(app, db)

# =====================================================
# PASSWORD HASHING
# =====================================================

bcrypt = Bcrypt(app)

# =====================================================
# LOGIN MANAGER
# =====================================================

login_manager = LoginManager(app)

login_manager.login_view = "login"

login_manager.login_message_category = "info"

# =====================================================
# EMAIL OBJECT
# =====================================================

mail = Mail(app)

# =====================================================
# IMPORT ROUTES
# =====================================================

from flaskblog import routes