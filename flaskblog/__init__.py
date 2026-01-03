import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# -------------------------------------------------
# App & Extensions
# -------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# -------------------------------------------------
# Logging Configuration (NO EMOJIS)
# -------------------------------------------------
if not os.path.exists("logs"):
    os.mkdir("logs")

file_handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=10240,
    backupCount=5
)

file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
)

file_handler.setLevel(logging.INFO)

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info("Flask application startup")

# -------------------------------------------------
# Import routes LAST
# -------------------------------------------------
from flaskblog import routes
