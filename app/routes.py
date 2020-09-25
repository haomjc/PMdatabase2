from flask_login import current_user, login_user, logout_user, login_required
from pyecharts.charts import Bar
from pyecharts.charts.basic_charts import pie, bar
from werkzeug.urls import url_parse

from app import app, db, db_manage
from flask import render_template, redirect, flash, url_for, request

from app.forms import LoginForm, RegistrationForm
from app.models import User

from pyecharts import options as opts
from pyecharts.charts import Pie
from pyecharts.faker import Faker


@app.route('/')
@app.route('/index')
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

    return render_template('pages/LOGIN/login-2.html', title='登录页', form=form)


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
    return render_template('pages/LOGIN/register-2.html', title='Register', form=form)


# @app.route('/user/<username>')
@app.route('/<username>')
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
    sql = "select id,name from user"
    datas = db_manage.query_data(sql)
    return render_template("pages/test/show_users.html", datas=datas)


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
        sql = "select * from suppliers where Region="+"'"+str(Region)+"'"+" and "+str(Material)+"='*'"

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


@app.route("/SearchByGrade")
def SearchByGrade():
    return render_template("pages/SEARCH BY GRADE/SearchByGrade.html")


@app.route("/DetailsofGrade", methods=['GET', 'POST'])
def DetailsofGrade():
    return render_template("pages/SEARCH BY GRADE/DetailsofGrade.html")



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