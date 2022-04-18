from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField
from wtforms.validators import DataRequired


class ImportForm(FlaskForm):
    file = FileField('Файл', validators=[DataRequired()])
    submit = SubmitField('Записать')
