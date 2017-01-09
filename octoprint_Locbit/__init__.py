from __future__ import absolute_import
from httplib import BadStatusLine
from .locbitNotifications import locbitMsgDict

import octoprint.plugin
import requests
import flask
import json


Layer = 0
uid = "55de667a295efb62093205e4"
# url = "http://192.168.0.34:3000"
#url = "http://api.locbit.com:8888/endpoint"
url = "https://test-api.locbit.com/endpoint"

class LocbitPlugin(octoprint.plugin.StartupPlugin,
			octoprint.plugin.TemplatePlugin,
			octoprint.plugin.SettingsPlugin,
			octoprint.plugin.EventHandlerPlugin,
			octoprint.plugin.AssetPlugin,
			octoprint.plugin.SimpleApiPlugin):


	def get_api_commands(self):
		return dict(
			command1=[],
			command2=["some_parameter"]
		)

	def on_api_command(self, command, data):
		import flask
		if command == "command1":
			parameter = "unset"
			if "parameter" in data:
				parameter = "set"
			self._logger.info("command1 called, parameter is {parameter}".format(**locals()))
		elif command == "command2":
			self._logger.info("command2 called, some_parameter is {some_parameter}".format(**data))

	def on_api_get(self, request):
                
                if request.args.get('settings') == '1':
                        
                        return_result = {}                 
                        
                        for qr_data_key in ['material', 'diameter', 'color', 'length', 'muid']:
                                return_result[qr_data_key] = self._settings.get([qr_data_key])
                        
                        return flask.jsonify(result=return_result)
                
		import subprocess
		output = subprocess.check_output(['/home/pi/oprint/lib/python2.7/site-packages'
										  '/octoprint_Locbit/qr.py'])
                json_output = json.loads(output)
                
                if 'error' in json_output:
                       return flask.jsonify(error=json_output['error']) 
                else:
                       qr_result = json_output.get('result')
                       
                       if qr_result is None:
                               return flask.jsonify(error="QR code read failure. Uknown error.") 
                       
                       qr_result = qr_result.split(",")
 
		       if len(qr_result) == 5:
                               return_result = {'material': qr_result[0],
                                                'diameter': qr_result[1],
                                                'color': qr_result[2],
                                                'length': qr_result[3],
                                                'muid': qr_result[4]}

                               octoprint.plugin.SettingsPlugin.on_settings_save(self, return_result)

                               try:
                                       post_data = {"MUID":return_result['muid'],
                                                    "Material":return_result['material'],
                                                    "Color":return_result['color'],
                                                    "Diameter":return_result['diameter'],
                                                    "Length":return_result['length']}

                                       post_result = requests.post(url, json=post_data, timeout=5)
                                       
                                       post_result.raise_for_status()

                                       post_result_data = post_result.json()

                                       if not post_result_data['success']:
                                               raise Exception("Post data: {}, response data: {}".format(str(post_data), str(post_result_data)))

 
                               except Exception as e:
                                       return flask.jsonify(result=return_result, locbit_error=str(e))

		               return flask.jsonify(result=return_result)
		       else:
		               return flask.jsonify(error="Invalid QR code") 

	def on_after_startup(self):
		self._logger.info("Hello world! I am: %s" % self._settings.get(["did"]))

	def get_settings_defaults(self):
		return dict(did="TEST_PRINTER",
                            material='',
                            diameter='',
                            color='',
                            length='',
                            muid='')

	def get_template_configs(self):
		return [
			dict(type="navbar", custom_bindings=False),
			dict(type="settings", custom_bindings=False)
		]

	def get_assets(self):
		return dict(js=["js/Locbit.js"])

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
