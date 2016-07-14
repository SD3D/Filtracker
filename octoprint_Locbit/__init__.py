from __future__ import absolute_import
from httplib import BadStatusLine
from .locbitNotifications import locbitMsgDict

import octoprint.plugin
import requests

Layer = 0
uid = "55de667a295efb62093205e4"
# url = "http://192.168.0.34:3000"
url = "http://api.locbit.com:8888/endpoint"

class LocbitPlugin(octoprint.plugin.StartupPlugin,
			octoprint.plugin.TemplatePlugin,
			octoprint.plugin.SettingsPlugin,
			octoprint.plugin.EventHandlerPlugin):
	
	def on_after_startup(self):
		self._logger.info("Hello world! I am: %s" % self._settings.get(["did"]))

	def get_settings_defaults(self):
		return dict(did="TEST_PRINTER")

	def get_template_configs(self):
		return [
			dict(type="navbar", custom_bindings=False),
			dict(type="settings", custom_bindings=False)
		]

	def on_event(self, event, payload, **kwargs):
		global Layer
		global uid
		global url
		did = self._settings.get(["did"])
		
		self.checkPrinterStatus()

		if event == "PrintStarted":
			Layer = 0
			self.sendLayerStatus(Layer)
		elif event == "PrintFailed":
			Layer = 0
			self.sendLayerStatus(Layer)
		elif event == "PrintCancelled":
			Layer = 0
			self.sendLayerStatus(Layer)

		if event in locbitMsgDict:
			event_body = {
				'uid' : uid,
				'did' : did,
				'event' : locbitMsgDict[event]['name'],
				'status' : locbitMsgDict[event]['value']
			}
		elif event == 'FileSelected':
			event_body = {
				'uid' : uid,
				'did' : did,
				'event' : 'File',
				'status' : payload['filename']
			}
		elif event == 'ZChange':
			Layer += 1
			event_body = {
				'uid' : uid,
				'did' : did,
				'event' : 'Layer',
				'status' : Layer
			}
		else:
			event_body = { 
				'uid' : uid,
				'did' : did,
				'event': event
			}

		try:
			requests.post(url, data = event_body)
		except BadStatusLine:
			self._logger.info("Locbit: Bad Status")

		self._logger.info("Locbit: Recording event " + event)

	def sendLayerStatus(self, layer):
		global uid
		global url
		did = self._settings.get(["did"])

		event_body = {
			'uid' : uid,
			'did' : did,
			'event' : 'Layer',
			'status' : layer
		}

		try:
			requests.post(url, data = event_body)
		except BadStatusLine:
			self._logger.info("Locbit: Bad Status")

	def checkPrinterStatus(self):
		url = "http://localhost/api/printer"
		apiKey = self._settings.get(["apiKey"])

		try:
			r = requests.get(url,  headers = { "X-Api-Key" : apiKey })
			self._logger.info(r.text)
		except BadStatusLine:
			self._logger.info("Locbit: Bad Status")


__plugin_name__ = "Locbit"
__plugin_implementation__ = LocbitPlugin()