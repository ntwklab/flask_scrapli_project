from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, SubmitField, RadioField, EmailField, StringField
from wtforms.validators import DataRequired


class DeviceForm(FlaskForm):
        ip = TextAreaField('IP Address of Device', validators=[DataRequired()])
        submit = SubmitField('Submit')
