from flask import Blueprint, render_template, redirect, url_for, session
from website.db_controller import DBcontroller
from website.devices.forms import DeviceForm
from website.devices.background_processes import CiscoCommands
from website.models import Devices


devices_blueprint = Blueprint('devices',__name__,
                                    template_folder='templates/devices')

@devices_blueprint.route('/info', methods = ['GET', 'POST'])
def info():

    form = DeviceForm()
    if form.validate_on_submit():
        # Split string on comma and append to a list
        session['ip'] = form.ip.data
        ips = session.get('ip', None).replace(" ", "").replace("\r\n\r\n", "").replace("\r\n", "").lower().split(',')

        # Uncomment below once list of IPs created
        error_ips = []
        show_ver = CiscoCommands()
        # hostname,ip,sw_version,model,os_type,chassis_sn,uptime = show_ver.show_version(ip)
        genie_list, error_ips = show_ver.create_threads(ips)

        # Add to DB
        device_inventory = DBcontroller()
        for device in genie_list:
            device_inventory.update_device_inventory(
                                                device['Hostname'], 
                                                device['IP'], 
                                                device['Version'], 
                                                device['Model'], 
                                                device['OS'], 
                                                device['Chassis'], 
                                                device['Uptime'])
        device_inventory.close_db_conn()

        all_devices = Devices.query.all()
        return render_template('inventory.html', all_devices=all_devices, error_ips=error_ips)
    
    else:
        form = DeviceForm()
        return render_template('info.html', form=form)



@devices_blueprint.route('/inventory')
def inventory():

    all_devices = Devices.query.all()

    return render_template('inventory.html', all_devices=all_devices)
