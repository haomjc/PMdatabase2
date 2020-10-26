from flask import request
from flask_babel import lazy_gettext as _l
from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email

from app.models import User


class PostForm(FlaskForm):
    # title = StringField('Title', validators=[DataRequired()])
    # body = CKEditorField('Body', validators=[DataRequired()])
    title = StringField('Title')
    body = CKEditorField('Body')
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)