from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, SubmitField, RadioField, EmailField, StringField
from wtforms.validators import DataRequired


class DeviceForm(FlaskForm):
        ip = TextAreaField('IP Address of Device', validators=[DataRequired()])
        submit = SubmitField('Submit')


class BaseConfigForm(FlaskForm):
        deviceType = RadioField('Device Type', choices=[('switch', 'Switch'), ('router','Router')], validators=[DataRequired()])
        os = RadioField('OS Type', choices=[('ios', 'IOS'), ('nexus','Nexus'), ('iosxe','IOS-XE')], validators=[DataRequired()])
        ip = StringField('IP Address', validators=[DataRequired()])
        subnet = StringField('Subnet Mask', validators=[DataRequired()])
        hostname = StringField('Hostname', validators=[DataRequired()])
        domainName = StringField('Domain Name', validators=[DataRequired()])
        mgmtInt = StringField('Management Interface or VLAN', validators=[DataRequired()])
        defaultRoute = StringField('Default Route', validators=[DataRequired()])
        enablePass = StringField('Enable Password', validators=[DataRequired()])
        submit = SubmitField('Submit')

class MulticastForm(FlaskForm):
        ip = TextAreaField('IP Addresses of Multicast Routers', validators=[DataRequired()])
        submit = SubmitField('Submit')
