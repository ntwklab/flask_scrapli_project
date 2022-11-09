from hashlib import new
from flask import Blueprint, render_template, redirect, url_for, session
from website.db_controller import DBcontroller
from website.devices.forms import DeviceForm, BaseConfigForm, MulticastForm
from website.devices.background_processes import CiscoCommands
from website.models import Devices, DeviceInfo
from datetime import datetime
import re

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
        genie_list, error_ips = show_ver.create_threads(ips, "show_version")

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


# Working
@devices_blueprint.route('/inventory')
def inventory():
    """
    Basic page that pulls in the database table for devices_table
    Added more to allow to determine if the time between device updates in greater than 200 seconds
    """

    all_devices = Devices.query.all()

    # Get last updated for all devices, if they are greater than 200 seconds say so!
    all_devices_updated = DeviceInfo.query.all()
    lastupdate = "Never"

    if all_devices_updated:
        compare_times = []
        for times in all_devices_updated:
            compare_times.append(times.updated)
        
        # Sort times in order
        compare_times.sort(key=lambda date: datetime.strptime(date, "%B, %d, %Y %H:%M:%S"))

        # Calculate the difference in seconds between top and bottom number
        tfirst = datetime.strptime(compare_times[0], "%B, %d, %Y %H:%M:%S")
        tlast = datetime.strptime(compare_times[-1], "%B, %d, %Y %H:%M:%S")
        difference = tlast - tfirst

        # If difference is les than 200 seconds, display last update as last date/time
        if difference.seconds < 200:
            lastupdate = tlast
        else:
            lastupdate = "More than 200 seconds between polling"
            
    return render_template('inventory.html', all_devices=all_devices, lastupdate=lastupdate)



@devices_blueprint.route('/<hostname>', methods = ['GET', 'POST'])
def device_info(hostname): # var hostname is required
    """
    Displays the details for the device
    Three tabs
    Tab1 basic info from devices_table
    Tab2 switchport info from device_details_table
    Tab3 show run output from device_details_table
    """
    
    # Get details to pass into template
    device_stats = DBcontroller()
    device_info = device_stats.get_device_basic_info(hostname)
    device_details = device_stats.get_device_details(hostname)
    print(device_info)

    if device_details != []:
        show_run = device_details[0][3].split('\n')
        lastupdate = device_details[0][8]
    else:
        show_run = "No Entry found, refresh data"
        lastupdate = "No Entry found, refresh data"
        device_details = "Empty"

    return render_template('detail.html', hostname=hostname, device_info=device_info, show_run=show_run, lastupdate=lastupdate, device_details=device_details)


# Working
@devices_blueprint.route('/details_<hostname>', methods = ['GET', 'POST'])
def get_device_details(hostname): # var hostname is required
    """
    Get the specific device details
    Same as the view bg_get_info, but single device
    Get IP, convert so it is in a list and send to "get_detailed" function of background_processes.py
    Redirect back to device detail page
    """

    # Get details to pass into template
    device_stats = DBcontroller()
    device_info = device_stats.get_device_basic_info(hostname)
    ip = [device_info[0][2]]

    # Perform show run
    get_detailed = CiscoCommands()
    genie_list, error_ips = get_detailed.create_threads(ip, "get_detailed")


    # Add new details to DB
    device_details = DBcontroller()

    # Delete all data in table for hostname
    device_details.delete_device_details(hostname)

    # Add new details to database
    for device in genie_list:
        device_details.update_device_details(
                                            device['Hostname'], 
                                            device['IP'], 
                                            device['Show run'],
                                            device['Physical Ports'],
                                            device['Virtual Ports'],
                                            device['Disabled Ports'],
                                            device['Enabled Ports'],
                                            device['Updated']
                                            )
    device_details.close_db_conn()

    return redirect(url_for('devices.device_info',hostname=hostname))


#Working
@devices_blueprint.route('/bg_get_info', methods = ['GET', 'POST'])
def bg_get_info():
    """
    Refreshes all decvices details
    Get current list of device IP addresses
    Perform commands in "get_detailed" function of background_processes.py
    Add them to the DB table
    """

    # Query DB Inventory table
    all_devices = Devices.query.all()

    # Create a device dictionary
    device_list = []
    for device in all_devices:
        device_dict = {"Hostname":device.hostname,
            "IP":device.ip
            } 
        device_list.append(device_dict)

    # Create IPs list to send to Scrapli
    ips = []
    for ip in device_list:
        ips.append(ip['IP'])

    # Perform show run
    get_detailed = CiscoCommands()
    genie_list, error_ips = get_detailed.create_threads(ips, "get_detailed")


    # Add to DB
    device_details = DBcontroller()

    # Delete all data in table
    device_details.delete_all_device_details()

    for device in genie_list:
        device_details.update_device_details( # Change this
                                            device['Hostname'], 
                                            device['IP'], 
                                            device['Show run'],
                                            device['Physical Ports'],
                                            device['Virtual Ports'],
                                            device['Disabled Ports'],
                                            device['Enabled Ports'],
                                            device['Updated']
                                            )
    device_details.close_db_conn()

    return redirect(url_for('devices.inventory'))




@devices_blueprint.route('/baseTemplate', methods = ['GET', 'POST'])
def baseTemplate():

    form = BaseConfigForm()
    if form.validate_on_submit():

        session['deviceType'] = form.deviceType.data
        session['os'] = form.os.data
        session['ip'] = form.ip.data
        session['subnet'] = form.subnet.data
        session['hostname'] = form.hostname.data
        session['domainName'] = form.domainName.data
        session['mgmtInt'] = form.mgmtInt.data
        session['defaultRoute'] = form.defaultRoute.data
        session['enablePass'] = form.enablePass.data


        if session['os'] == 'ios' or 'iosxe':
            if session['deviceType'] == 'switch':
                config = (f"hostname {session['hostname']}\n"
                        f"ip domain name {session['domainName']}\n"
                        f"no ip domain-lookup\n"
                        f"!\n"
                        f"interface Vlan1\n"
                        f"ip address {session['ip']} {session['subnet']}\n"
                        f"no shut\n"
                        f"!\n"
                        f"crypto key generate rsa general-keys modulus 1024\n"
                        f"!\n"
                        f"line vty 0  4\n"
                        f"password Stefan2020\n"
                        f"privilege level 15\n"
                        f"transport input ssh\n"
                        f"!\n"
                        f"aaa new-model\n"
                        f"username admin password 0 Stefan2020\n"
                        f"!\n"
                        f"enable secret 0 {session['enablePass']}\n"
                        f"ip route 0.0.0.0 0.0.0.0 {session['defaultRoute']}")

            if session['deviceType'] == 'router':
                config = (f"hostname {session['hostname']}\n"
                        f"ip domain name {session['domainName']}\n"
                        f"no ip domain-lookup\n"
                        f"!\n"
                        f"interface {session['mgmtInt']}\n"
                        f"ip address {session['ip']} {session['subnet']}\n"
                        f"no shut\n"
                        f"!\n"
                        f"crypto key generate rsa general-keys modulus 1024\n"
                        f"!\n"
                        f"line vty 0  15\n"
                        f"password Stefan2020\n"
                        f"login local\n"
                        f"privilege level 15\n"
                        f"transport input ssh\n"
                        f"!\n"
                        f"aaa new-model\n"
                        f"username admin password 0 Stefan2020\n"
                        f"!\n"
                        f"enable secret 0 {session['enablePass']}\n"
                        f"ip route 0.0.0.0 0.0.0.0 {session['defaultRoute']}")

        if session['os'] == 'nexus':
            config = (f"hostname {session['hostname']}\n"
                        f"ip domain-name {session['domainName']}\n"
                        f"crypto key generate rsa modulus 1024\n"
                        f"!\n"
                        f"interface {session['mgmtInt']}\n"
                        f"vrf member management\n"
                        f"ip address {session['ip']} {session['subnet']}\n"
                        f"!\n"
                        f"username admin password 0 Stefan2020\n"
                        f"vrf context management\n"
                        f"ip route 0.0.0.0 0.0.0.0 {session['defaultRoute']}\n")

        config = config.split("\n")
        config_list = []
        for line in config:
            config_list.append(line)


        return render_template('baseTemplateOutput.html', config_list=config_list)
    
    else:
        form = BaseConfigForm()
        return render_template('baseTemplate.html', form=form)


@devices_blueprint.route('/multicast', methods = ['GET', 'POST'])
def multicast():
    form = MulticastForm() 
    
    if form.validate_on_submit():
        form_IPs = {'mcast_routers':[form.data]}
        
        # Gather IPs from form to pass into another page
        session["form_IPs"]=form_IPs
        return  redirect(url_for('devices.bg_get_mroute'))

    else:
        return render_template('multicast.html', form=form)


@devices_blueprint.route('/bg_get_mroute', methods = ['GET', 'POST'])
def bg_get_mroute():
    """
    Gets the multicast routing table and parses it
    """

    # Get form values
    form_IPs = session.get("form_IPs", None)
    ips = form_IPs['mcast_routers'][0]['ip'].replace(" ", "").replace("\r\n\r\n", "").replace("\r\n", "").split(',')
    
    # ips = ["172.16.1.115","172.16.1.116","172.16.1.117","172.16.1.118"]
    # Perform show ip mroute
    get_detailed = CiscoCommands()
    genie_list, error_ips = get_detailed.create_threads(ips, "show_mroute")

    show_output_dict = {}
    parsed_output = []
    
    for device in genie_list:
        
        for key, value in device.items():
            if key != "show_output":
                print("\n")
                print(f"Hostname: {key}")
                show_output_dict.update({key:re.split('\n\n|\n|\n\n\n',device['show_output'])})
                parsed_output.append({key:value})

        print(parsed_output)

    return render_template('bg_get_mroute.html', show_output_dict=show_output_dict, parsed_output=parsed_output)
