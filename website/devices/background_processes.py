from scrapli.driver.core import IOSXEDriver, NXOSDriver
import queue
from threading import Thread


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

            
    def create_threads(self, ips):
        cmd = CiscoCommands()

        q = queue.Queue()
        genie_list = []
        error_ips = []

        for thread_no in range(8):
            worker = Thread(target=cmd.show_version, args=(q, genie_list, error_ips, ), daemon=True)
            worker.start()

        for ip in ips:
            q.put(ip)

        q.join()

        return genie_list, error_ips
