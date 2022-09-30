import sqlite3
import os

class DBcontroller:

	def __init__(self):
		#self.connection = connection
		self.basedir = os.path.abspath(os.path.dirname(__file__))
		self.connection = sqlite3.connect(self.basedir+'/data.sqlite')


	def update_device_inventory(self, hostname, ip, sw_version, model, os_type, chassis_sn, uptime):
		"""
		Appends data to the device table
		"""	
		cursor = self.connection.cursor()

		cursor.execute("INSERT INTO devices_table\
						(hostname, ip, sw_version, model, os_type, chassis_sn, uptime) VALUES (?,?,?,?,?,?,?)",
						(hostname, ip, sw_version, model, os_type, chassis_sn, uptime) )
		self.connection.commit()


	def close_db_conn(self):
		self.connection.close()
