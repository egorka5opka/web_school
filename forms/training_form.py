from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField
from wtforms.validators import DataRequired


class TrainingForm(FlaskForm):
    year = IntegerField('Год', validators=[])
    submit = SubmitField('Проверить')
