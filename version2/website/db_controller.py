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



	def update_device_details(self, hostname, ip, showrun, physicalports, virtualports, disabledports, enabledports, updated):
		"""
		Appends data to the device table
		"""	
		cursor = self.connection.cursor()

		cursor.execute("INSERT INTO device_details_table\
						(hostname, ip, showrun, physicalports, virtualports, disabledports, enabledports, updated) VALUES (?,?,?,?,?,?,?,?)",
						(hostname, ip, showrun, physicalports, virtualports, disabledports, enabledports, updated) )
		self.connection.commit()
	


	def close_db_conn(self):
		self.connection.close()




	def get_device_basic_info(self, hostname):
		"""
		Retrieve info from ALL switches in devices_table.
		"""
		sql = "SELECT * FROM devices_table WHERE hostname = ?;"
		cur = self.connection.cursor()
		cur.execute(sql, [hostname])
		result = cur.fetchall()
		return result

	def get_device_details(self, hostname):
		"""
		Retrieve info from ALL switches in device_details_table.
		"""
		sql = "SELECT * FROM device_details_table WHERE hostname = ?;"
		cur = self.connection.cursor()
		cur.execute(sql, [hostname])
		result = cur.fetchall()
		return result


	# Working
	def delete_device_details(self, hostname):
		"""
		This deletes all the table entries for the hostname
		"""
		sql = "DELETE FROM device_details_table WHERE hostname = ?;"
		cur = self.connection.cursor()
		cur.execute(sql, [hostname])
		self.connection.commit()


	# Working
	def delete_all_device_details(self):
		"""
		F5 Info Table
		Delete all rows in the device_details_table table
		:param connection: Connection to the SQLite database
		:return:
		"""
		sql = 'DELETE FROM device_details_table'
		cur = self.connection.cursor()
		cur.execute(sql)
		self.connection.commit()