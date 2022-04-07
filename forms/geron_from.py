from flask_wtf import FlaskForm
from wtforms import SubmitField, FloatField
from wtforms.validators import DataRequired


class GeronForm(FlaskForm):
    first_number = FloatField('Первая сторона', validators=[DataRequired()])
    second_number = FloatField('Вторая сторона', validators=[DataRequired()])
    third_number = FloatField('Третья сторона', validators=[DataRequired()])
    submit = SubmitField('Площадь')