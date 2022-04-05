from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField
from wtforms.validators import DataRequired


class FactorizationForm(FlaskForm):
    number = IntegerField('Число', validators=[DataRequired()])
    submit = SubmitField('Разложить')