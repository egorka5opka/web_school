from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, StringField
from wtforms.validators import DataRequired


class TranslateForm(FlaskForm):
    first_number = StringField('Первое число', validators=[DataRequired()])
    first_step = IntegerField('Основание системы изначальной', validators=[DataRequired()])
    second_step = IntegerField('Основание системы итоговой', validators=[DataRequired()])
    submit = SubmitField('Перевести')