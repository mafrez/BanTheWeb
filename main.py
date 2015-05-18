# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtCore, QtGui, uic
import pwd, grp
import pickle, operator
from os.path import expanduser
import os


idstart = 1000
form_class = uic.loadUiType("ui/main.ui")[0]	# Load the main UI
dial1 = uic.loadUiType("ui/dial1.ui")[0]		# Load the UI for profile managing
assign = uic.loadUiType("ui/assign.ui")[0]		# Load the UI for profile assign
stats = uic.loadUiType("ui/stats.ui")[0]		# Load the UI for profile assign

class StatsForm(QtGui.QDialog, stats):

	def __init__(self, parent=None):
		global idstart
		QtGui.QWidget.__init__(self, parent)
		self.setupUi(self)
		self.data = parent.data
		self.parent = parent
		stats_text = ""
		for p in pwd.getpwall():
			if p[2] >= idstart:
				home = p[5]
				try:
					user_stats = pickle.load(open(home+"/.tk_stats.p", "rb"))
					stats_text = stats_text + p[0] + "\n"
					for a in user_stats:
						if ('date' in user_stats[a]):
							stats_text = stats_text + user_stats[a]['date'] + " - " + str(user_stats[a]['time']) + " minutes" + "\n"
					stats_text = stats_text + "\n"
				except:
					pass
		self.textEdit.setText(stats_text)

class AssignForm(QtGui.QDialog, assign):

	def __init__(self, parent=None, assign_type = None, uuid = 0):
		QtGui.QWidget.__init__(self, parent)
		self.setupUi(self)
		self.data = parent.data
		self.assign_type = assign_type
		self.uuid = int(uuid)
		self.parent = parent
		#print self.assign_type, uuid
		for i in self.data['profiles']:
		  self.comboBox.insertItem(int(self.data['profiles'][i]['id']),self.data['profiles'][i]['id']+"|"+self.data['profiles'][i]['name'])
	######################################################################################
	# Accept assigning profile		  
	def accept(self):
		profile_id =  int(self.comboBox.currentText().split("|")[0])
		if (self.assign_type == "user"):
			self.data['user_profiles'][self.uuid] = profile_id
			
		# For groups
		if (self.assign_type == "group"):
			self.data['group_profiles'][self.uuid] = profile_id
		
		self.parent.distribute_configs()
		
		self.close()

class MyForm(QtGui.QDialog, dial1):

	def __init__(self, parent=None, id_profile = None):
		QtGui.QWidget.__init__(self, parent)
		self.setupUi(self)
		self.data = parent.data
		
		#print parent.data['profiles']
		self.id_profile = id_profile
		#print self.id_profile
		#QtCore.QObject.connect(self.ui.pushButton, QtCore.SIGNAL('clicked()'), self.popup)	 
		if (id_profile):
			self.load_data()

	######################################################################################
	# Combobox settings in dialog
	def set_combobox(self,combo,val):
		val = str(val)
		index = combo.findText(val)
		if(index != -1):
			combo.setCurrentIndex(index)

	######################################################################################
	# Load profile data in dialog
	def load_data(self):
	  
		self.name.setText(self.data['profiles'][self.id_profile]['name'])
		#self.set_combobox(self.no_type,self.data['profiles'][self.id_profile]['not'])
		#self.set_combobox(self.no_interval,self.data['profiles'][self.id_profile]['noi'])
		#self.set_combobox(self.logout_type,self.data['profiles'][self.id_profile]['lot'])

		self.set_combobox(self.SocialNetworks,self.data['profiles'][self.id_profile]['SN'])
		self.set_combobox(self.HideProfanity,self.data['profiles'][self.id_profile]['HP'])
		self.set_combobox(self.AdultContent,self.data['profiles'][self.id_profile]['AC'])
		self.set_combobox(self.SafeSearch,self.data['profiles'][self.id_profile]['SS'])

		self.BlackList.setText(self.data['profiles'][self.id_profile]['BL'])
		self.WhiteList.setText(self.data['profiles'][self.id_profile]['WL'])

		sett = self.data['profiles'][self.id_profile]['settings']
		self.su_banned.setText(sett[1]['banned'])
		self.mo_banned.setText(sett[2]['banned'])
		self.tu_banned.setText(sett[3]['banned'])
		self.we_banned.setText(sett[4]['banned'])
		self.th_banned.setText(sett[5]['banned'])
		self.fr_banned.setText(sett[6]['banned'])
		self.sa_banned.setText(sett[7]['banned'])

		for a in range(7):
			index = a + 1
			if (index == 1):
			  comboH = self.su_hours
			  comboM = self.su_mins
			elif (index == 2):
			  comboH = self.mo_hours
			  comboM = self.mo_mins
			elif (index == 3):
			  comboH = self.tu_hours
			  comboM = self.tu_mins
			elif (index == 4):
			  comboH = self.we_hours
			  comboM = self.we_mins
			elif (index == 5):
			  comboH = self.th_hours
			  comboM = self.th_mins
			elif (index == 6):
			  comboH = self.fr_hours
			  comboM = self.fr_mins
			elif (index == 7):
			  comboH = self.sa_hours
			  comboM = self.sa_mins

			if(sett[index]['time'] != "None"):
				self.set_combobox(comboH, int(sett[index]['time']) / 60)
				self.set_combobox(comboM, int(sett[index]['time']) % 60)

	######################################################################################
	# Create new profile with data model
	def new_profile(self,new_id):
		name = self.name.text()

		SN = str(self.SocialNetworks.currentText())
		HP = str(self.HideProfanity.currentText())
		AC = str(self.AdultContent.currentText())
		SS = str(self.SafeSearch.currentText())

		BL =  str(self.BlackList.toPlainText())
		WL =  str(self.WhiteList.toPlainText())

		su_banned = self.su_banned.text()
		mo_banned = self.mo_banned.text()
		tu_banned = self.tu_banned.text()
		we_banned = self.we_banned.text()
		th_banned = self.th_banned.text()
		fr_banned = self.fr_banned.text()
		sa_banned = self.sa_banned.text()
		
		su_time = str(int(self.su_hours.currentText())*60+int(self.su_mins.currentText()))
		mo_time = str(int(self.mo_hours.currentText())*60+int(self.mo_mins.currentText()))
		tu_time = str(int(self.tu_hours.currentText())*60+int(self.tu_mins.currentText()))
		we_time = str(int(self.we_hours.currentText())*60+int(self.we_mins.currentText()))
		th_time = str(int(self.th_hours.currentText())*60+int(self.th_mins.currentText()))
		fr_time = str(int(self.fr_hours.currentText())*60+int(self.fr_mins.currentText()))
		sa_time = str(int(self.sa_hours.currentText())*60+int(self.sa_mins.currentText()))

		print SN

		# Profile data model
		self.data['profiles'][new_id] = {"id" : str(new_id), "name" : name, "SN" : SN, "HP" : HP, "AC" : AC, "SS" : SS, "WL" : WL, "BL" : BL ,"settings" : {
								1 : {"banned" : su_banned, "time" : su_time}, 
								2 : {"banned" : mo_banned, "time" : mo_time}, 
								3 : {"banned" : tu_banned, "time" : tu_time}, 
								4 : {"banned" : we_banned, "time" : we_time}, 
								5 : {"banned" : th_banned, "time" : th_time}, 
								6 : {"banned" : fr_banned, "time" : fr_time}, 
								7 : {"banned" : sa_banned, "time" : sa_time}
							}}
	######################################################################################
	# Save settings for existing profile or create new one
	def accept(self):
		if not (self.id_profile):
			new_id = max(self.data['profiles'].iteritems(), key=operator.itemgetter(0))[0]+1
			# print "Adding new profile with ID:",new_id
			self.new_profile(new_id)
		else:
			# print "Editing profile with ID:",self.id_profile
			self.new_profile(self.id_profile)
		self.close()


class MyWindowClass(QtGui.QMainWindow, form_class):
	def __init__(self, parent=None):
		self.data = self.reload_data()
		QtGui.QMainWindow.__init__(self, parent)
		self.setupUi(self)
		self.actionQuit.triggered.connect(self.quit)
		#self.actionStatistics.triggered.connect(self.show_stats)
		self.btn_profiles_edit.clicked.connect(self.edit_profiles)
		self.btn_profiles_add.clicked.connect(self.add_profiles)
		self.btn_profiles_delete.clicked.connect(self.delete_profiles)
		self.btn_uprofiles_assign.clicked.connect(self.edit_user_profiles)
		self.btn_uprofiles_delete.clicked.connect(self.delete_user_profiles)
		self.btn_gprofiles_assign.clicked.connect(self.edit_group_profiles)
		self.btn_gprofiles_delete.clicked.connect(self.delete_group_profiles)
		self._dialog = None
		
		self.fill_profiles()
		self.fill_user_profiles()
		self.fill_group_profiles()

	######################################################################################
	# Reload settings with 2 test profiles
	def reload_data(self):
		all_data = {'profiles' :
						{5 :
							{"id" : "5", "name" : "Employee", "SN" : "Allowed", "HP" : "Yes", "AC" : "Allowed", "SS" : "Allowed", "WL" : "", "BL" : "", "settings" : {
								1 : {"banned" : "1230-1630", "time" : "60"}, 
								2 : {"banned" : "1330-1730", "time" : "50"}, 
								3 : {"banned" : "1430-2355", "time" : "40"}, 
								4 : {"banned" : "1530-2355", "time" : "30"}, 
								5 : {"banned" : "1630-2030", "time" : "20"}, 
								6 : {"banned" : "1730-2130", "time" : "10"}, 
								7 : {"banned" : "1830-2230", "time" : "10"}
							}},
						6 :
							{"id" : "6", "name" : "Childrens", "SN" : "Allowed", "HP" : "Yes", "AC" : "Allowed", "SS" : "Allowed", "WL" : "", "BL" : "", "settings" : {
								1 : {"banned" : "1230-1630", "time" : "80"}, 
								2 : {"banned" : "1330-1730", "time" : "70"}, 
								3 : {"banned" : "1430-1830", "time" : "60"}, 
								4 : {"banned" : "1530-1930", "time" : "50"}, 
								5 : {"banned" : "1630-2030", "time" : "40"}, 
								6 : {"banned" : "1730-2130", "time" : "30"}, 
								7 : {"banned" : "1830-2230", "time" : "20"}
							}}
						},
					'user_profiles' :
						{},
					'group_profiles' :
						{}
					}
		# Only for testing
		#pickle.dump(all_data, open("config.p", "wb"))
		return pickle.load(open("config.p", "rb"))
	######################################################################################
	# Redistribute all config files
	def distribute_configs(self):
		global idstart
		for p in pwd.getpwall():
			if p[2] >= idstart:
				home = p[5]
				# If user has set profile id, then copy settings
				if (int(p[2]) in self.data['user_profiles']):
					profile_id = self.data['user_profiles'][int(p[2])]
					profile_settings = self.data['profiles'][profile_id]
					try:
						pickle.dump(profile_settings, open(home+"/.btw_settings.p", "wb"))
					except:
						pass
				elif (int(p[3]) in self.data['group_profiles']):
					profile_id = self.data['group_profiles'][int(p[3])]
					profile_settings = self.data['profiles'][profile_id]
					try:
						pickle.dump(profile_settings, open(home+"/.btw_settings.p", "wb"))
					except:
						pass
				else:
					try:
						pickle.dump({}, open(home+"/.btw_settings.p", "wb"))
					except:
						pass

				try:
					os.chown(home+"/.btw_settings.p", p[2], p[3])
				except:
					pass
	######################################################################################
	# Saves main app pickle file
	def save_data(self):
		pickle.dump( self.data, open( "config.p", "wb" ) )
		#return pickle.load( open( "config.p", "rb" ) )
	######################################################################################
	# Filling profile table with data
	def fill_profiles(self):
		# Read all filters from PICKEL and show
		self.table_profiles.setRowCount(0)
		entries = []
		for a in self.data['profiles']:
			entries.append((self.data['profiles'][a]['id'],self.data['profiles'][a]['name']))

		self.table_profiles.setRowCount(len(entries))
		self.table_profiles.setColumnCount(len(entries[0]))
		for i, row in enumerate(entries):
			for j, col in enumerate(row):
				item = QtGui.QTableWidgetItem(col)
				self.table_profiles.setItem(i, j, item)
	######################################################################################
	# Edit existing profile for time managemant
	def edit_profiles(self):
		prof_row = self.table_profiles.currentIndex().row()
		# If profile is selected in table
		if (prof_row >= 0):
			pass
			# print "Editing profile ID:",self.table_profiles.item(prof_row,0).text()
		else:
			return
		id_prof = int(self.table_profiles.item(prof_row,0).text())
		myapp= MyForm(self,id_prof)
		myapp.exec_()
		self.save_data()
		self.fill_profiles()
		self.distribute_configs()
	######################################################################################
	# Delete profiles - recursively with all settings
	def delete_profiles(self):
		prof_row = self.table_profiles.currentIndex().row()
		# If profile is selected in table
		if (prof_row >= 0):
			pass
			# print "Delete profile ID:",self.table_profiles.item(prof_row,0).text()
		else:
			return
		
		pid = int(self.table_profiles.item(prof_row,0).text())
		del self.data['profiles'][pid]
		
		self.save_data()
		self.fill_profiles()
		self.distribute_configs()
	######################################################################################
	# Add new profile
	def add_profiles(self):
		myapp= MyForm(self,None)
		myapp.exec_()
		self.save_data()
		self.fill_profiles()
	######################################################################################
	# Filling profile table with data
	def fill_user_profiles(self):
		global idstart
		# Find all users and by user ID read pickle and assign
		self.table_user_profiles.setRowCount(0)
		entries = []
		for p in pwd.getpwall():
			if p[2] >= idstart:
				# If user has set profile id, then find name
				user_profile_name = ""
				group_profile_name = ""
				effective_profile_name = ""

				if (int(p[2]) in self.data['user_profiles']):
					user_profile_id = self.data['user_profiles'][int(p[2])]
					user_profile_name = self.data['profiles'][user_profile_id]['name']
					effective_profile_name = user_profile_name
				if (int(p[3]) in self.data['group_profiles']):
					group_profile_id = self.data['group_profiles'][int(p[3])]
					group_profile_name = self.data['profiles'][group_profile_id]['name']
					if (effective_profile_name == ""):
						effective_profile_name = group_profile_name
				entries.append((str(p[2]),p[0],user_profile_name, group_profile_name, effective_profile_name))
		
		# Read all filters from PICKEL and show
		self.table_user_profiles.setRowCount(len(entries))
		self.table_user_profiles.setColumnCount(len(entries[0]))
		for i, row in enumerate(entries):
			for j, col in enumerate(row):
				item = QtGui.QTableWidgetItem(col)
				self.table_user_profiles.setItem(i, j, item)
	#####################################################################################
	# Edit existin profile for time managemant
	def edit_user_profiles(self):
		prof_row = self.table_user_profiles.currentIndex().row()
		# If profile is selected in table
		if (prof_row >= 0):
			pass
			# print "Editing user filter settings:",self.table_user_profiles.item(prof_row,0).text()
		else:
			return
		myapp= AssignForm(self,"user",self.table_user_profiles.item(prof_row,0).text())
		myapp.exec_()
		self.save_data()
		self.fill_user_profiles()
		self.distribute_configs()
	#####################################################################################	
	# Delete profiles - recursively with all settings
	def delete_user_profiles(self):
		prof_row = self.table_user_profiles.currentIndex().row()
		# If profile is selected in table
		if (prof_row >= 0):
			pass
			# print "Delete user filter settings:",self.table_user_profiles.item(prof_row,0).text()
		else:
			return

		pid = int(self.table_user_profiles.item(prof_row,0).text())
		del self.data['user_profiles'][pid]

		self.save_data()
		self.fill_user_profiles()
		self.distribute_configs()
	#####################################################################################
	# Filling profile table with data
	def fill_group_profiles(self):
		global idstart
		# Find all groups and by group ID read pickle and assign
		self.table_group_profiles.setRowCount(0)
		entries = []
		for p in pwd.getpwall():
			if p[2] >= idstart:
				# If group has set profile id, then find name
				group_profile_name = ""
				if (int(p[2]) in self.data['group_profiles']):
					  group_profile_id = self.data['group_profiles'][int(p[2])]
					  group_profile_name = self.data['profiles'][group_profile_id]['name']
				entries.append((str(p[2]),p[0],group_profile_name))
		
		# Read all filters from PICKEL and show
		self.table_group_profiles.setRowCount(len(entries))
		self.table_group_profiles.setColumnCount(len(entries[0]))
		for i, row in enumerate(entries):
			for j, col in enumerate(row):
				item = QtGui.QTableWidgetItem(col)
				self.table_group_profiles.setItem(i, j, item)
	#####################################################################################
	# Edit existing profile for time managemant
	def edit_group_profiles(self):
		prof_row = self.table_group_profiles.currentIndex().row()
		# If profile is selected in table
		if (prof_row >= 0):
			pass
			# print "Editing group filter settings:",self.table_group_profiles.item(prof_row,0).text()
		else:
			return
		myapp= AssignForm(self,"group",self.table_group_profiles.item(prof_row,0).text())
		myapp.exec_()
		self.save_data()
		self.fill_group_profiles()
		self.fill_user_profiles()
		self.distribute_configs()
	#####################################################################################
	# Delete profiles - recursively with all settings
	def delete_group_profiles(self):
		prof_row = self.table_group_profiles.currentIndex().row()

		# If profile is selected in table
		if (prof_row >= 0):
			pass
			# print "Delete group filter settings:",self.table_group_profiles.item(prof_row,0).text()
		else:
			return

		pid = int(self.table_group_profiles.item(prof_row,0).text())
		del self.data['group_profiles'][pid]

		self.save_data()
		self.fill_group_profiles()
		self.fill_user_profiles()
		self.distribute_configs()
	#####################################################################################
	def quit(self):
		print "exit"
		sys.exit()

	def show_stats(self):
		myapp= StatsForm(self)
		myapp.exec_()

	def show_dial1(self):
		myapp= MyForm(self)
		myapp.show()
 
app = QtGui.QApplication(sys.argv)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()
