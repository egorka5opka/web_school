from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField
from wtforms.validators import DataRequired


class TranslateForm(FlaskForm):
    first_number = IntegerField('Первое число', validators=[DataRequired()])
    first_step = IntegerField('Основание системы', validators=[DataRequired()])
    second_number = IntegerField('Второе число', validators=[DataRequired()])
    second_step = IntegerField('Основание системы', validators=[DataRequired()])
    submit = SubmitField('Перевести')