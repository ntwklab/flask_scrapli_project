from scrapli.driver.core import IOSXEDriver, NXOSDriver
import queue
from threading import Thread
from datetime import datetime
from scrapli.helper import textfsm_parse
import os

basedir = os.path.abspath(os.path.dirname(__file__)) 


class CiscoCommands:

    def __init__(self):
        self.username = 'admin'
        self.password = 'Stefan2020'


    def conn(self, ip):

        switch = {
            "host": ip,
            "auth_username":self.username,
            "auth_password":self.password,
            "auth_strict_key":False,
            # "auth_bypass": True,
            "transport": "paramiko",
            "timeout_ops": 2, 
            "timeout_socket": 1, 
            "timeout_transport": 1
        }

        try: 
            host = IOSXEDriver(**switch)
            host.open()
            os = "ios"

        except:
            host = NXOSDriver(**switch)
            host.open()
            os = "nxos"

        return host, os


    def show_version(self, q, genie_list, error_ips):
        while True:
            ip = q.get()
            
            try:
                host, os = CiscoCommands.conn(self, ip)
            except:
                error_ips.append(ip)
                q.task_done()
                break

            output = host.send_command("show version")

            # Genie Parsed Response
            genie_parsed_response = output.genie_parse_output()

            if os == "ios":
                hostname = genie_parsed_response['version']['hostname']
                ip = ip
                sw_version = genie_parsed_response['version']['version']
                try:
                    model = genie_parsed_response['version']['chassis']
                except:
                    model = "Unknown"
                os_type = genie_parsed_response['version']['os']
                chassis_sn = genie_parsed_response['version']['chassis_sn']
                uptime = genie_parsed_response['version']['uptime']

                genie_dict = {"Hostname":hostname,
                            "IP":ip,
                            "Version":sw_version,
                            "Model":model,
                            "OS":os_type,
                            "Chassis":chassis_sn,
                            "Uptime":uptime
                            } 
                genie_list.append(genie_dict) 

            elif os == "nxos":
                hostname = genie_parsed_response['platform']['hardware']['device_name']
                ip = ip
                sw_version = genie_parsed_response['platform']['software']['system_version']
                try:
                    model = genie_parsed_response['platform']['hardware']['model']
                except:
                    model = "Unknown"
                os_type = genie_parsed_response['platform']['os']
                chassis_sn = genie_parsed_response['platform']['hardware']['processor_board_id']
                uptimed = genie_parsed_response['platform']['kernel_uptime']['days']
                uptimeh = genie_parsed_response['platform']['kernel_uptime']['hours']
                uptimem = genie_parsed_response['platform']['kernel_uptime']['minutes']

                uptime = f"{uptimed} days, {uptimeh} hours, {uptimem} minutes"

                genie_dict = {"Hostname":hostname,
                            "IP":ip,
                            "Version":sw_version,
                            "Model":model,
                            "OS":os_type,
                            "Chassis":chassis_sn,
                            "Uptime":uptime
                            } 
                genie_list.append(genie_dict)

            q.task_done()              


    def get_detailed(self, q, genie_list, error_ips):
        while True:
            ip = q.get()
            
            try:
                host, os = CiscoCommands.conn(self, ip)
            except:
                error_ips.append(ip)
                q.task_done()
                break

            # perforn show run and get hostname from prompt
            output = host.send_command("show run")
            prompt = host.get_prompt()

            # Show interface details
            if os == "ios":
                shipintbr = host.send_command("show interfaces")
            elif os == "nxos":
                shipintbr = host.send_command("show interface")
            
            genie_parsed_response = shipintbr.genie_parse_output()

            # Display number of port types
            physical_int = 0
            virtual_int = 0

            for interface in genie_parsed_response.keys():
                if "Ethernet" in interface:
                    physical_int +=1
                if "Vlan" in interface:
                    virtual_int +=1

            # Add to database
            print("\n")
            print(physical_int)
            print(virtual_int)

            
            # Display Port Status
            shut_ports = 0
            noshut_ports = 0
            if os == "ios":
                for interface in genie_parsed_response.keys():
                    if genie_parsed_response[interface]['enabled'] == True:
                        noshut_ports +=1
                    elif genie_parsed_response[interface]['enabled'] == False:
                        shut_ports +=1
            elif os == "nxos":
                for interface in genie_parsed_response.keys():
                    if genie_parsed_response[interface]['admin_state'] == "up":
                        noshut_ports +=1
                    elif genie_parsed_response[interface]['admin_state'] == "down":
                        shut_ports +=1                
            
            # Add to database
            print("\n")
            print(f"Shutdown Ports: {shut_ports}")
            print(f"Enabled Ports: {noshut_ports}")


            # Get time
            now = datetime.now()
            timestamp = now.strftime("%B, %d, %Y %H:%M:%S")

            # Create list of dictionaries to be returned
            genie_dict = {"Hostname":prompt[:-1],
                        "IP":ip,
                        "Show run":output.result,
                        "Physical Ports": physical_int,
                        "Virtual Ports": virtual_int,
                        "Disabled Ports": shut_ports,
                        "Enabled Ports": noshut_ports,
                        "Updated":timestamp
                        } 
            genie_list.append(genie_dict)

            q.task_done()


    def create_threads(self, ips, user_command):
        """
        views.py sends the user_command
        """
        q = queue.Queue()
        genie_list = []
        error_ips = []

        # Take in the "command" from the view and convert to a functional call
        send_cmd = getattr(CiscoCommands(), user_command)

        
        # Create multithreading
        for thread_no in range(8):
            worker = Thread(target=send_cmd, args=(q, genie_list, error_ips, ), daemon=True)
            worker.start()

        # Start the threads
        for ip in ips:
            q.put(ip)

        q.join()

        return genie_list, error_ips


    def show_mroute(self, q, genie_list, error_ips):
        while True:
            ip = q.get()

            # Check IOS Type   
            try:
                host, os = CiscoCommands.conn(self, ip)
                print(f"host: {host}, OS: {os}")
            except:
                error_ips.append(ip)
                print(f"Error connecting to: {ip}")
                q.task_done()
                break

            # Show ip mroute details
            if os == "ios":
                output = host.send_command("show ip mroute")
                prompt = host.get_prompt()
            elif os == "nxos":
                prompt = host.get_prompt()
                output = host.send_command("show ip mroute")

                print("\n")

                # TextFSM parse response
                textfsm_template = basedir +'/textfsm/nxos_mroute.textfsm'
                textfsm_parsed_response = textfsm_parse(textfsm_template, output.result)

                # Create a list of dictionaries to return
                device_dict = {prompt[:-1]:[textfsm_parsed_response][0], 
                                'show_output':output.result}
                genie_list.append(device_dict)

            q.task_done()


if __name__ == '__main__':
    self = CiscoCommands()
    # error_ips = CiscoCommands.show_mroute(self, q, genie_list, error_ips)

    """
    mcast_nexus1: 172.16.1.115,
    mcast_nexus2: 172.16.1.116,
    mcast_nexus3: 172.16.1.117,
    mcast_nexus4: 172.16.1.118
    """

    ips = ["172.16.1.115","172.16.1.116","172.16.1.117","172.16.1.118"]

    genie_list, error_ips = CiscoCommands.create_threads(self, ips, "show_mroute")