from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from flask_babel import _
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(url_for('index'))

    return render_template('pages/LOGIN/login.html', title='登录页', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('pages/LOGIN/register.html', title='Register', form=form)


@bp.route('/user/<username>')
# @app.route('/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', title='主页', user=user)


@bp.route('/show_add_user')
def show_add_user():
    return render_template('pages/test/show_add_user.html')


@bp.route("/do_add_user", methods=['POST'])
def do_add_user():
    print(request.form)
    name = request.form.get("name")
    sex = request.form.get("sex")
    age = request.form.get("age")
    email = request.form.get("email")

    sql = f"""
    insert into user (name,sex,age,email)
    values ('{name}','{sex}',{age},'{email}')

"""
    print(sql)
    db_manage.insert_or_update_data(sql)
    return 'success'


@bp.route("/show_users")
def show_users():
    form = PostForm()
    sql = "select id,name from user"
    datas = db_manage.query_data(sql)
    return render_template("pages/test/show_users.html", datas=datas, form=form)


@bp.route("/show_user/<user_id>")
def show_user(user_id):
    sql = "select * from user where id=" + user_id
    datas = db_manage.query_data(sql)
    user = datas[0]
    return render_template("pages/test/show_user.html", user=user)

