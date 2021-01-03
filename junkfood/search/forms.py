from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, IntegerField, validators, SubmitField
from wtforms.validators import ValidationError, DataRequired, URL, Optional
from flask import current_app


class SearchForm(FlaskForm):
    transcript = StringField('Transcript', validators=[DataRequired()])
    speakers = SelectField('Speaker', validators=[Optional()])
    episode = IntegerField('Episode', validators=[Optional()])
    submit = SubmitField('Search')
