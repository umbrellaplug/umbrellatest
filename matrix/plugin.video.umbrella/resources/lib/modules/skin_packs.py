# -*- coding: utf-8 -*-
"""
	Umbrella Add-on (added by Umbrella Dev 01/07/23)
"""

from resources.lib.modules import control
from resources.lib.modules import log_utils
import os

getLS = control.lang
getSetting = control.setting
LOGINFO = 1

class iconPackHandler:
	name = "iconPack"
	def __init__(self):
		self.hosters = None

	def show_skin_packs(self):
		from resources.lib.modules import log_utils
		log_utils.log('Show window for icons packs here.', 1)
		try:
			control.busy()
			self.list = self.get_skin_packs()
			control.hide()
			from resources.lib.windows.icon_packs import IconPacksView
			window = IconPacksView('icon_packs.xml', control.addonPath(control.addonId()), results=self.list)
			selected_items = window.run()
			del window
			if selected_items:
				from resources.lib.modules import log_utils
				log_utils.log('selected items: %s' % str(selected_items), 1)
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			control.hide()

	def get_skin_packs(self):
		self.list1 = []
		from resources.lib.modules import log_utils
		log_utils.log('Get local skin packs.', 1)
		directory = control.iconFolders()
		subfolders = [ f.name for f in os.scandir(directory) if f.is_dir() ]
		#we need to walk the directory now and get all the pre-installed skin packs
		from resources.lib.modules import log_utils
		log_utils.log('directory is %s' % subfolders, 1)
		from resources.lib.modules import log_utils
		log_utils.log('Get skin packs from github.', 1)
		try:
			import re
			import requests
			repo_xml = requests.get('https://raw.githubusercontent.com/umbrellaplug/umbrellaplug.github.io/master/matrix/xml/skinpack/Skins.xml')
			if not repo_xml.status_code == 200:
				return control.log('[ plugin.video.umbrella ]  Could not connect to remote repo XML: status code = %s' % repo_xml.status_code, LOGINFO)
		#minidom will need to be used here to parse the list from xml.
		except:
			from resources.lib.modules import log_utils
			log_utils.log('Error getting skin packs from github.', 1)
		return self.list1