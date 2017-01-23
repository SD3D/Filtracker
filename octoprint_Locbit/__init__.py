from __future__ import absolute_import, division
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
status_url = 'https://test-api.locbit.com/statusByLid'

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

        def _post_spool_data(self, spool_data):
                
                post_data = {"MUID":spool_data['muid'],
                             "Material":spool_data['material'],
                             "Color":spool_data['color'],
                             "Diameter":spool_data['diameter'],
                             "Length":spool_data['length']}

                post_result = requests.post(url, json=post_data, timeout=5)

                post_result.raise_for_status()

                post_result_data = post_result.json()

                if not post_result_data['success']:
                        raise Exception("Post data: {}, response data: {}".format(str(post_data), str(post_result_data)))

        def _get_spool_length(self, muid):

                locbit_api_key = self._settings.get(['locbitAPIKey'])
                locbit_access_id = self._settings.get(['locbitAccessID'])

                if len(locbit_api_key) == 0 or len(locbit_access_id) == 0:
                        raise Exception("Cannot get stored spool length, either locbit api key or access ID is missing from settings")

                request_uri = "{}/{}/SD3DPrinter".format(status_url, muid)

                query_params = {'api': locbit_api_key, 'access': locbit_access_id} 

                response = requests.get(request_uri, params=query_params, timeout=5)

                response.raise_for_status()

                response_data = response.json()

                if 'measurements' in response_data:
                        length = response_data['measurements']['Length']['status']
                        return length
                elif 'success' in response_data and \
                      not response_data['success'] and \
                      response_data['message'] == 'Device is not found':
                        return None
                else:
                        raise Exception("Spool length lookup failed, uknown error. Response: {}".format(str(response_data)))

        def _get_spool_settings(self):

                setting_keys = ['muid', 'material', 'color', 'diameter', 'length', 'initial_length']

                setting_dict = {}

                for setting_key in setting_keys:

                        setting_value = self._settings.get([setting_key])

                        if setting_value is None or len(setting_value) == 0:
                                raise Exception("Setting {} is not set".format(setting_key))

                        setting_dict[setting_key] = setting_value

                return setting_dict 

        def _get_printer_job_info(self):
                job_uri = 'http://localhost/api/job'
                octoprint_api_key = self._settings.get(["apiKey"])
       
                assert octoprint_api_key is not None and len(octoprint_api_key) > 0

                response = requests.get(job_uri,  headers = { "X-Api-Key" : octoprint_api_key }, timeout=1)
                response.raise_for_status()

                return response.json()

        def _update_spool_length(self, update_remote=False):

                try:
                        current_spool_settings = self._get_spool_settings()
                        
                        printer_job_info = self._get_printer_job_info()

                        initial_length = float(current_spool_settings['initial_length'])

                        job_obj = printer_job_info.get('job')
                        filament_obj = None
                        tool0_obj = None
                        estimated_job_length = None
                        job_completion_percent = None
                        
                        if job_obj is not None:
                                filament_obj = job_obj.get('filament')

                        if filament_obj is not None:
                                tool0_obj = filament_obj.get('tool0')

                        if tool0_obj is not None:
                                estimated_job_length = tool0_obj['length']

                        progress_obj = printer_job_info.get('progress')

                        if progress_obj is not None:
                                job_completion_percent = progress_obj['completion'] 

                        if job_completion_percent is not None:

                                # Job filament length is in millimeters, so must convert to meters
                                length_job_used = (job_completion_percent / 100) * (estimated_job_length / 1000)

                                new_length = initial_length - length_job_used

                                current_spool_settings['length'] = new_length

                                if update_remote:
                                        self._post_spool_data(current_spool_settings)

                                current_spool_settings['length'] = str(current_spool_settings['length'])

                                octoprint.plugin.SettingsPlugin.on_settings_save(self, current_spool_settings)
                except Exception as e:
                        self._logger.error("Could not update length: {}".format(str(e)))

	def on_api_get(self, request):
                
                if request.args.get('settings') == '1':
                        
                        return_result = {}                 
                        
                        for qr_data_key in ['material', 'diameter', 'color', 'length', 'muid']:
                                return_result[qr_data_key] = self._settings.get([qr_data_key])
                        
                        return_result['length'] = "{0:.3f}".format(float(return_result['length'])) 
                        return flask.jsonify(result=return_result)
                
		import subprocess
   
                horizontal_flip = self._settings.get(['camFlipHorizontal'])

                qr_script_path = '/home/pi/oprint/lib/python2.7/site-packages/octoprint_Locbit/qr.py'
                subprocess_args = [qr_script_path]

                output = ''
                
                if horizontal_flip:
                        subprocess_args.append('-f')
                
                output = subprocess.check_output(subprocess_args)
                
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
                               
                               # Initialize plugin settings with data from QR code
                               octoprint.plugin.SettingsPlugin.on_settings_save(self, return_result)
                               octoprint.plugin.SettingsPlugin.on_settings_save(self, {'initial_length': return_result['length']})

                               try:

                                       stored_length = self._get_spool_length(return_result['muid'])

                                       # If the length of the spool already exists, update the settings,
                                       # otherwise, post the initial spool data
                                       if stored_length is not None:
                                               return_result['length'] = stored_length
                                               octoprint.plugin.SettingsPlugin.on_settings_save(self, return_result)
                                               octoprint.plugin.SettingsPlugin.on_settings_save(self, {'initial_length': return_result['length']})
                                       else:
                                               self._post_spool_data(return_result)

                               except Exception as e:
                                       return flask.jsonify(result=return_result, locbit_error=str(e))

                               return_result['length'] = "{0:.3f}".format(float(return_result['length'])) 

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
                            initial_length='',
                            length='',
                            muid='',
                            locbitAPIKey='',
                            locbitAccessID='',
                            camFlipHorizontal=False)

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
                        current_spool_settings = self._get_spool_settings()
                        current_spool_settings['initial_length'] = current_spool_settings['length']
                        octoprint.plugin.SettingsPlugin.on_settings_save(self, current_spool_settings)
                        self._update_spool_length(update_remote=True)
                        print('^' * 20 + current_spool_settings['initial_length'])
		elif event == "PrintFailed":
			Layer = 0
			self.sendLayerStatus(Layer)
                        current_spool_settings = self._get_spool_settings()
                        current_spool_settings['initial_length'] = current_spool_settings['length']
                        octoprint.plugin.SettingsPlugin.on_settings_save(self, current_spool_settings)
		elif event == "PrintCancelled":
			Layer = 0
			self.sendLayerStatus(Layer)
                        current_spool_settings = self._get_spool_settings()
                        current_spool_settings['initial_length'] = current_spool_settings['length']
                        octoprint.plugin.SettingsPlugin.on_settings_save(self, current_spool_settings)
                        print('&' * 30) 
                elif event == "PrintDone":
                        current_spool_settings = self._get_spool_settings()
                        current_spool_settings['initial_length'] = current_spool_settings['length']
                        octoprint.plugin.SettingsPlugin.on_settings_save(self, current_spool_settings)
                        pass
                elif event == "PrintPaused":
                        self._update_spool_length(update_remote=True)
                        
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
                        self._update_spool_length(update_remote=True)
		else:
			event_body = {
				'uid' : uid,
				'did' : did,
				'event': event
			}

                        self._update_spool_length(update_remote=False)

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
