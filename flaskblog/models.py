from datetime import datetime
from flask import current_app
from itsdangerous import Serializer
from sqlalchemy import desc
from flaskblog import db, bcrypt, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    password_history = db.relationship('PasswordHistory', backref='user', lazy=True)

    def get_verification_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt=current_app.config['SECURITY_PASSWORD_SALT'])
    
    @staticmethod
    def verify_verification_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=expires_sec)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt=current_app.config['SECURITY_PASSWORD_SALT'])

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=expires_sec)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def update_password_history(self, new_password):
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        if not self.password_history:
            self.password_history = []
        self.password_history.append(PasswordHistory(user_id=self.id, password_hash=hashed_password))
        db.session.commit()

    def check_password_history(self, candidate_password):
        recent_passwords = PasswordHistory.query.filter_by(user_id=self.id).order_by(desc(PasswordHistory.timestamp)).limit(5).all()
        for password_entry in recent_passwords:
            if bcrypt.check_password_hash(password_entry.password_hash, candidate_password):
                return True
        return False

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class PasswordHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
