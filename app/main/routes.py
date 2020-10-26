from datetime import datetime
from random import randrange
import os

from flask_babel import get_locale
from flask_login import current_user, login_user, logout_user, login_required
from pyecharts.charts import Bar
from pyecharts.charts.basic_charts import pie, bar, line
from werkzeug.urls import url_parse

from app import app, db, db_manage
from flask import render_template, redirect, flash, url_for, request, send_from_directory, current_app

from app.forms import LoginForm, RegistrationForm, PostForm, SearchForm
from app.models import User, Post, Detail

from pyecharts import options as opts
from pyecharts.charts import Pie, Line
from flask_ckeditor import upload_success, upload_fail

from pyecharts.faker import Faker
from flask import g
from app.main import bp

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['CKEDITOR_SERVE_LOCAL'] = True
app.config['CKEDITOR_HEIGHT'] = 400
app.config['CKEDITOR_FILE_UPLOADER'] = 'upload'
# app.config['CKEDITOR_ENABLE_CSRF'] = True  # if you want to enable CSRF protect, uncomment this line


app.secret_key = 'secret string'


@app.route('/')
@app.route('/index')
@login_required
def index():
    # user = User.query.filter_by(username=username).first_or_404()
    # return redirect('app/templates/index.html')
    return render_template('index.html', title='主页')


@app.route('/login', methods=['GET', 'POST'])
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


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
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


@app.route('/user/<username>')
# @app.route('/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', title='主页', user=user)


@app.route('/show_add_user')
def show_add_user():
    return render_template('pages/test/show_add_user.html')


@app.route("/do_add_user", methods=['POST'])
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


@app.route("/show_users")
def show_users():
    form = PostForm()
    sql = "select id,name from user"
    datas = db_manage.query_data(sql)
    return render_template("pages/test/show_users.html", datas=datas, form=form)


@app.route("/show_user/<user_id>")
def show_user(user_id):
    sql = "select * from user where id=" + user_id
    datas = db_manage.query_data(sql)
    user = datas[0]
    return render_template("pages/test/show_user.html", user=user)


@app.route("/show_echarts")
def show_echarts():
    bar = (
        Bar()
            .add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
            .add_yaxis("商家A", [5, 20, 36, 10, 75, 90])
    )
    return render_template("pages/test/show_echarts.html",
                           bar_options=bar.dump_options()
                           )


def get_pie() -> pie:
    sql = """
        select sex,count(1) as cnt from user group by sex
    """
    datas = db_manage.query_data(sql)
    c = (
        Pie()
            .add("", [(data['sex'], data['cnt']) for data in datas])
            .set_global_opts(title_opts=opts.TitleOpts(title="Pie-基本示例"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    return c


def get_bar() -> bar:
    sql = """
        select sex,count(1) as cnt from user group by sex
    """
    datas = db_manage.query_data(sql)
    c = (
        Bar()
            .add_xaxis([data['sex'] for data in datas])
            .add_yaxis("数量", [data['cnt'] for data in datas])
            .set_global_opts(title_opts=opts.TitleOpts(title="Pie-基本示例", subtitle="Pie-基本示例"))
    )
    return c


@app.route("/show_myecharts")
def show_myecharts():
    pie = get_pie()
    bar = get_bar()

    return render_template("pages/test/show_myecharts.html",
                           pie_options=pie.dump_options(),
                           bar_options=bar.dump_options()
                           )


@app.route("/SNFatigueData")
def SNFatigueData():
    return render_template("pages/FATIGUEDATA/SN Fatigue Data.html")


@app.route("/StrainLifeData")
def StrainLifeData():
    return render_template("pages/FATIGUEDATA/Strain Life Data.html")


@app.route("/supplierReport", methods=['GET', 'POST'])
def supplierReport():
    return render_template("pages/LINKTOSUPPLIERS/supplierReport.html")


@app.route("/SUPPLIERLIST", methods=['GET', 'POST'])
def SUPPLIERLIST():
    Region = request.form.get('Region')
    Material = request.form.get('Material')
    if Material == 'All':
        sql = "select * from suppliers where Region=" + "'" + str(Region) + "'"
    else:
        sql = "select * from suppliers where Region=" + "'" + str(Region) + "'" + " and " + str(Material) + "='*'"

    datas_pmsuppliers = db_manage.query_data(sql)

    return render_template("pages/LINKTOSUPPLIERS/SUPPLIERLIST.html", datas_pmsuppliers=datas_pmsuppliers)


@app.route("/aboutmetalinjectionmoulding")
def aboutmetalinjectionmoulding():
    return render_template("pages/PMinformation/aboutmetalinjectionmoulding.html")


@app.route("/aboutpowdermetallurgy")
def aboutpowdermetallurgy():
    return render_template("pages/PMinformation/aboutpowdermetallurgy.html")


@app.route("/DesignationCodes")
def DesignationCodes():
    return render_template("pages/PMinformation/DesignationCodes.html")


@app.route("/manufacturingconditions")
def manufacturingconditions():
    return render_template("pages/PMinformation/manufacturingconditions.html")


@app.route("/SearchonMechanicalProperties")
def SearchonMechanicalProperties():
    return render_template("pages/searchbyproperties/SearchonMechanicalProperties.html")


@app.route("/MechanicalProperties", methods=['GET', 'POST'])
def MechanicalProperties():
    manufacturingtechnology = request.form.get('manufacturing technology')
    materialtype = request.form.get('material type')
    UltimateTensileStrengthRange = request.form.get('Ultimate Tensile Strength Range')
    YieldStressRange = request.form.get('Yield Stress Range')
    YoungsModulusERange = request.form.get('Youngs Modulus E Range')
    HardnessRangeVickers = request.form.get('Hardness Range [Vickers]')

    return render_template("pages/searchbyproperties/MechanicalProperties.html")


@app.route("/SearchonPhysicalandMagneticProperties")
def SearchonPhysicalandMagneticProperties():
    return render_template("pages/searchbyproperties/SearchonPhysicalandMagneticProperties.html")


@app.route("/PhysicalandMagneticProperties", methods=['GET', 'POST'])
def PhysicalandMagneticProperties():
    return render_template("pages/searchbyproperties/PhysicalandMagneticProperties.html")


@app.route("/SearchonFatigueProperties")
def SearchonFatigueProperties():
    return render_template("pages/searchbyproperties/SearchonFatigueProperties.html")


@app.route("/FatigueProperties", methods=['GET', 'POST'])
def FatigueProperties():
    return render_template("pages/searchbyproperties/FatigueProperties.html")


@app.route("/SearchByGradePowderMetallurgy")
def SearchByGradePowderMetallurgy():
    return render_template("pages/SEARCH BY GRADE/SearchByGradePowderMetallurgy.html")


@app.route("/SearchByGradePlastic")
def SearchByGradePlastic():
    return render_template("pages/SEARCH BY GRADE/SearchByGradePlastic.html")


def get_line(sql, xaxis_name, yaxis_name) -> Line:
    datas = db_manage.query_data(sql)
    # datas_pr = db_manage.query_data(sql_pr)
    # print(list(data.values()) for data in datas)
    c = (
        Line()
            .add_xaxis(
            [list(data.values())[0] for data in datas]
        )
            .add_yaxis(
            series_name="",
            y_axis=[list(data.values())[1] for data in datas],
            is_smooth=True,
            label_opts=opts.LabelOpts(is_show=False),
        )
            .set_global_opts(
            xaxis_opts=opts.AxisOpts(name=xaxis_name, type_="value", position="middle"),
            yaxis_opts=opts.AxisOpts(name=yaxis_name, type_="value", position="middle"),
        )
    )
    return c


@app.route("/DetailsofGrade/<gradeNum>/<densityNum>/<pages>", methods=['GET', 'POST'])
def DetailsofGrade(gradeNum, densityNum, pages):
    app.config['UPLOADED_PATH'] = os.path.join(basedir, '../Data/uploads/', gradeNum)

    title = str(gradeNum)
    body = Detail.query.filter(Detail.title == gradeNum).first()
    form = PostForm(title=gradeNum, body=body.text)
    # form = PostForm(title=gradeNum)

    # print(form.validate_on_submit())
    # if form.validate_on_submit():
    title = form.title.data
    new_body = form.body.data
    # detail = Detail(title=title, text=body)
    body.text = str(new_body)
    db.session.commit()

    # WARNING: use bleach or something similar to clean the data (escape JavaScript code)
    # You may need to store the data in database here
    grade = request.form.get('Grade')
    density = request.form.get('Density')
    if grade is None:
        grade = gradeNum
    if density is None:
        density = densityNum
    pages = pages
    # print(grade, pages)
    # print(densityNum)
    if str(densityNum) == "plastic":
        sql_ss = "select 应变" + pages + ",应力" + pages + " from " + str(grade) + "_ss"
        sql_ss_num = "select count(1) from information_schema.COLUMNS where TABLE_SCHEMA='python_mysql' and " \
                     "TABLE_NAME='" + str(grade) + "_ss'"
    else:
        sql_ss = "select 应变" + pages + ",应力" + pages + " from " + str(grade) + str(density) + "_ss"
        sql_ss_num = "select count(1) from information_schema.`COLUMNS` where TABLE_SCHEMA='python_mysql' and " \
                     "TABLE_NAME='" + str(grade) + str(density) + "_ss'"
    sql_pr = "select 轴向伸长量,横向减少量 from " + str(grade) + "_pr"

    ss_num = db_manage.query_data(sql_ss_num)
    ss_num = [list(num.values())[0] for num in ss_num]
    ss_num = ss_num[0] // 2
    # print(ss_num)
    line_ss = get_line(sql_ss, "应变", "应力")
    if str(densityNum) == "plastic":
        line_pr = get_line(sql_pr, "轴向伸长量", "横向减少量")

        return render_template("pages/SEARCH BY GRADE/DetailsofGrade.html",
                               line_options_ss=line_ss.dump_options(),
                               line_options_pr=line_pr.dump_options(),
                               gradeNum=grade,
                               densityNum=density,
                               ssNum=ss_num,
                               form=form,
                               title=title,
                               body=body.text
                               )
    else:
        return render_template("pages/SEARCH BY GRADE/DetailsofGrade.html",
                               line_options_ss=line_ss.dump_options(),
                               gradeNum=grade,
                               densityNum=density,
                               ssNum=ss_num,
                               form=form,
                               title=title,
                               body=body.text
                               )


@app.route("/PropertySearch")
def PropertySearch():
    return render_template("pages/ADVANCED SEARCH/PropertySearch.html")


@app.route("/ShowSavedSearch")
def ShowSavedSearch():
    return render_template("pages/ADVANCED SEARCH/ShowSavedSearch.html")


@app.route("/ClearsTheSavedSearch")
def ClearsTheSavedSearch():
    return render_template("pages/ADVANCED SEARCH/ClearsTheSavedSearch.html")


@app.route("/ViewLastSearchResults")
def ViewLastSearchResults():
    return render_template("pages/ADVANCED SEARCH/ViewLastSearchResults.html")


@app.route("/help_on_plotting")
def help_on_plotting():
    return render_template("pages/help/help_on_plotting.html")


@app.route("/help_on_reports")
def help_on_reports():
    return render_template("pages/help/help_on_reports.html")


@app.route("/help")
def help():
    return render_template("pages/help/help.html")


@app.route("/view_data_cart")
def view_data_cart():
    return render_template("pages/data/view_data_cart.html")


@app.route("/empty_data_cart")
def empty_data_cart():
    return render_template("pages/data/empty_data_cart.html")


@app.route("/SelectPropertiesForCrossPlot")
def SelectPropertiesForCrossPlot():
    return render_template("pages/PLOT/SelectPropertiesForCrossPlot.html")


@app.route("/ShowCrossPlot", methods=['GET', 'POST'])
def ShowCrossPlot():
    return render_template("pages/PLOT/ShowCrossPlot.html")


@app.route('/files/<filename>')
def uploaded_files(filename):
    path = app.config['UPLOADED_PATH']
    return send_from_directory(path, filename)


@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')
    extension = f.filename.split('.')[-1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg', 'pdf']:
        return upload_fail(message='Image only!')
    f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
    url = url_for('uploaded_files', filename=f.filename)
    return upload_success(url=url)



@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())



@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=_('Search'), posts=posts,
                           next_url=next_url, prev_url=prev_url)
