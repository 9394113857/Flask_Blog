import os
import secrets
from datetime import datetime
from PIL import Image

from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import (
    RegistrationForm, LoginForm,
    UpdateAccountForm, PostForm,
    RequestResetForm, ResetPasswordForm
)
from flaskblog.models import (
    User, Post,
    PostLike, Comment,
    UserEvent
)

# ==================================================
# HELPERS
# ==================================================
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    i = Image.open(form_picture)
    i.thumbnail((125, 125))
    i.save(picture_path)

    return picture_fn


def log_event(user_id, event_type, object_type, object_id):
    db.session.add(UserEvent(
        user_id=user_id,
        event_type=event_type,
        object_type=object_type,
        object_id=object_id
    ))
    db.session.commit()


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        'Password Reset Request',
        sender='noreply@demo.com',
        recipients=[user.email]
    )
    msg.body = f'''
To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request, simply ignore this email.
'''
    mail.send(msg)

# ==================================================
# HOME
# ==================================================
@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)

    if current_user.is_authenticated:
        log_event(current_user.id, "feed_view", "feed", 0)

    return render_template("home.html", posts=posts)

# ==================================================
# USER POSTS
# ==================================================
@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()

    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)

    return render_template("user_posts.html", posts=posts, user=user)

# ==================================================
# ABOUT
# ==================================================
@app.route("/about")
def about():
    return render_template("about.html", title="About")

# ==================================================
# AUTH
# ==================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash("Account created. You can now login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("home"))
        flash("Login unsuccessful.", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

# ==================================================
# PASSWORD RESET (🔥 FINAL FIX 🔥)
# ==================================================
@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("Password reset email sent.", "info")
        return redirect(url_for("login"))

    return render_template("reset_request.html", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    user = User.verify_reset_token(token)
    if user is None:
        flash("Invalid or expired token", "warning")
        return redirect(url_for("reset_request"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_pw
        db.session.commit()
        flash("Password updated!", "success")
        return redirect(url_for("login"))

    return render_template("reset_token.html", form=form)

# ==================================================
# POSTS
# ==================================================
@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Post created!", "success")
        return redirect(url_for("home"))
    return render_template("create_post.html", form=form)


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    likes = PostLike.query.filter_by(post_id=post.id).count()
    comments = Comment.query.filter_by(post_id=post.id, parent_id=None).all()
    return render_template("post.html", post=post, likes=likes, comments=comments)


@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.", "success")
    return redirect(url_for("home"))

# ==================================================
# LIKE & COMMENT
# ==================================================
@app.route("/post/<int:post_id>/like", methods=["POST"])
@login_required
def like_post(post_id):
    like = PostLike.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if like:
        db.session.delete(like)
    else:
        db.session.add(PostLike(user_id=current_user.id, post_id=post_id))
    db.session.commit()
    return redirect(url_for("post", post_id=post_id))


@app.route("/post/<int:post_id>/comment", methods=["POST"])
@login_required
def add_comment(post_id):
    db.session.add(Comment(
        content=request.form.get("content"),
        user_id=current_user.id,
        post_id=post_id
    ))
    db.session.commit()
    return redirect(url_for("post", post_id=post_id))
