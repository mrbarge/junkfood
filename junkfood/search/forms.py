from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, IntegerField, validators, SubmitField
from wtforms.validators import ValidationError, DataRequired, URL, Optional
from flask import current_app


class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()], id='search_autocomplete')
    submit = SubmitField('Search')
