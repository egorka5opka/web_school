from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired


class CreateTableForm(FlaskForm):
    expression = StringField('Выражание', validators=[DataRequired()])
    submit = SubmitField('Построить')