import os
import secrets
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
from flaskblog.models import User, Post, PostLike, Comment

# ==================================================
# HELPERS
# ==================================================
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, "static/profile_pics", picture_fn)

    img = Image.open(form_picture)
    img.thumbnail((125, 125))
    img.save(picture_path)

    return picture_fn


def send_verification_email(user):
    token = user.get_verification_token()
    msg = Message(
        "Verify Your Email",
        sender="noreply@demo.com",
        recipients=[user.email]
    )
    msg.body = f"""
Verify your email:
{url_for('verify_email', token=token, _external=True)}
"""
    mail.send(msg)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        "Password Reset",
        sender="noreply@demo.com",
        recipients=[user.email]
    )
    msg.body = f"""
Reset your password:
{url_for('reset_token', token=token, _external=True)}
"""
    mail.send(msg)

# ==================================================
# HOME
# ==================================================
@app.route("/")
@app.route("/home")
def home():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("home.html", posts=posts)

# ==================================================
# SINGLE POST
# ==================================================
@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    likes = PostLike.query.filter_by(post_id=post.id).count()
    comments = Comment.query.filter_by(post_id=post.id).all()
    return render_template("post.html", post=post, likes=likes, comments=comments)

# ==================================================
# LIKE POST  🔥 FIX
# ==================================================
@app.route("/post/<int:post_id>/like", methods=["POST"])
@login_required
def like_post(post_id):
    like = PostLike.query.filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()

    if like:
        db.session.delete(like)
    else:
        db.session.add(PostLike(
            user_id=current_user.id,
            post_id=post_id
        ))

    db.session.commit()
    return redirect(url_for("post", post_id=post_id))

# ==================================================
# ADD COMMENT  🔥 FIX
# ==================================================
@app.route("/post/<int:post_id>/comment", methods=["POST"])
@login_required
def add_comment(post_id):
    content = request.form.get("content")
    if content:
        db.session.add(Comment(
            content=content,
            user_id=current_user.id,
            post_id=post_id
        ))
        db.session.commit()
    return redirect(url_for("post", post_id=post_id))

# ==================================================
# USER POSTS
# ==================================================
@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get("page", 1, type=int)
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
    return render_template("about.html")

# ==================================================
# REGISTER
# ==================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_pw,
            verified=False
        )
        db.session.add(user)
        db.session.commit()
        send_verification_email(user)
        flash("Account created! Check your email to verify.", "info")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)

# ==================================================
# VERIFY EMAIL
# ==================================================
@app.route("/verify_email/<token>")
def verify_email(token):
    user = User.verify_verification_token(token)
    if not user:
        flash("Invalid or expired link.", "danger")
        return redirect(url_for("login"))

    user.verified = True
    db.session.commit()
    flash("Email verified successfully!", "success")
    return redirect(url_for("login"))

# ==================================================
# LOGIN / LOGOUT
# ==================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if not user.verified:
                flash("Verify email before login.", "warning")
                return redirect(url_for("login"))
            login_user(user)
            return redirect(url_for("home"))
        flash("Login failed.", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

# ==================================================
# ACCOUNT
# ==================================================
@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.picture.data:
            current_user.image_file = save_picture(form.picture.data)
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Account updated!", "success")
        return redirect(url_for("account"))

    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for("static", filename="profile_pics/" + current_user.image_file)
    return render_template("account.html", image_file=image_file, form=form)

# ==================================================
# NEW POST
# ==================================================
@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash("Post created!", "success")
        return redirect(url_for("home"))

    return render_template("create_post.html", form=form)

# ==================================================
# PASSWORD RESET
# ==================================================
@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("Reset email sent.", "info")
        return redirect(url_for("login"))
    return render_template("reset_request.html", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    user = User.verify_reset_token(token)
    if not user:
        flash("Invalid token.", "danger")
        return redirect(url_for("reset_request"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        db.session.commit()
        flash("Password updated!", "success")
        return redirect(url_for("login"))

    return render_template("reset_token.html", form=form)
