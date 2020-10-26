from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config
from flask import Flask, current_app
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask import request
from elasticsearch import Elasticsearch
from flask import Blueprint
from flask_babel import Babel

bootstrap = Bootstrap()
db = SQLAlchemy()
ckeditor = CKEditor()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
babel = Babel()


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


def create_app(config_class=Config):
    app = Flask(__name__)

    ctx = app.app_context()
    ctx.push()
    print(current_app.name)

    app.config.from_object(Config)
    app.elasticsearch = Elasticsearch([current_app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    ckeditor.init_app(app)
    babel.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app


from app import models

