from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField
from wtforms.validators import DataRequired


class GcdForm(FlaskForm):
    first_number = IntegerField('Первое число', validators=[DataRequired()])
    second_number = IntegerField('Второе число', validators=[DataRequired()])
    submit = SubmitField('НОД и НОК')