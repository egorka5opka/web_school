from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class EventForm(FlaskForm):
    year = IntegerField('Год', validators=[DataRequired()])
    event = StringField('Название')
    description = TextAreaField('Описание')
    submit = SubmitField('Записать')
