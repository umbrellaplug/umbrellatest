# -*- coding: utf-8 -*-
"""
	Umbrella Add-on
"""

from json import dumps as jsdumps
from resources.lib.modules.control import dialog, getSourceHighlightColor, addonIcon
from resources.lib.windows.base import BaseDialog

class ProgressResolve(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.window_id = 2085
		self.closed = False
		self.meta = kwargs.get('meta')
		self.icon = addonIcon()

	def run(self):
		self.doModal()
		self.clearProperties()

	def onInit(self):
		self.set_controls()

	def onAction(self, action):
		if action in self.closing_actions or action in self.selection_actions:
			self.doClose()

	def doClose(self):
		self.closed = True
		self.close()
		del self
  
	def iscanceled(self):
		return self.closed

	def set_controls(self):
		if self.meta.get('clearlogo'): self.setProperty('umbrella.clearlogo', self.meta.get('clearlogo'))
		if self.meta.get('fanart'): self.setProperty('umbrella.fanart', self.meta.get('fanart'))
		if self.meta.get('title'): self.setProperty('umbrella.title', self.meta.get('title'))
		if 'tvshowtitle' in self.meta: self.setProperty('umbrella.tvtitle', self.meta.get('tvshowtitle'))
		if self.meta.get('plot'): self.setProperty('umbrella.plot', self.meta.get('plot', ''))
		self.setProperty('umbrella.highlight.color', getSourceHighlightColor())
		self.getControl(200).setImage(self.icon)
		self.getControl(201).setImage(self.icon)

	def update(self, percent=0, content='', icon=None):
		try:
			self.getControl(2001).setText(content)
			self.getControl(5000).setPercent(percent)
			if icon: self.getControl(200).setImage(icon)
		except: pass