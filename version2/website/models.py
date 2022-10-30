from website import db

class Devices(db.Model):

    __tablename__ = 'devices_table'
    id = db.Column(db.Integer,primary_key=True)
    hostname = db.Column(db.Text)
    ip = db.Column(db.Text)
    sw_version = db.Column(db.Text)
    model = db.Column(db.Text)
    os_type = db.Column(db.Text)
    chassis_sn = db.Column(db.Text)
    uptime = db.Column(db.Text)

    def __repr__(self):
        return f"You selected: : {self.hostname}, IP is: {self.ip}, OS family is : {self.os_type}"


class DeviceInfo(db.Model):
    # Add in new colums for more details
    __tablename__ = 'device_details_table'
    id = db.Column(db.Integer,primary_key=True)
    hostname = db.Column(db.Text)
    ip = db.Column(db.Text)
    showrun = db.Column(db.Text)
    physicalports = db.Column(db.Text)
    virtualports = db.Column(db.Text)
    disabledports = db.Column(db.Text)
    enabledports = db.Column(db.Text)
    updated = db.Column(db.Text)