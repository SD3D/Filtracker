from __future__ import absolute_import, division
from httplib import BadStatusLine
from .locbitNotifications import locbitMsgDict

import octoprint.plugin
from octoprint.slicing import SlicingManager, UnknownProfile
from octoprint.server import printerProfileManager
from octoprint.settings import settings
import requests
import flask
from flask import request
import json
import hashlib
import os
from shutil import copyfile
import urllib
from urlparse import urlsplit

Layer = 0
uid = "55de667a295efb62093205e4"
# url = "http://192.168.0.34:3000"
#url = "http://api.locbit.com:8888/endpoint"
url = "https://test-api.locbit.com/endpoint"
status_url = 'https://test-api.locbit.com/statusByLid'

HTTP_REQUEST_TIMEOUT=30

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

                post_result = requests.post(url, json=post_data, timeout=HTTP_REQUEST_TIMEOUT)

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

                response = requests.get(request_uri, params=query_params, timeout=HTTP_REQUEST_TIMEOUT)

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

                setting_keys = ['muid', 'material', 'color', 'diameter', 'length', 'initial_length', 'jobProgress']

                setting_dict = {}

                for setting_key in setting_keys:

                        setting_value = self._settings.get([setting_key])

                        setting_dict[setting_key] = setting_value

                return setting_dict 

        def _get_printer_job_info(self):
                job_uri = 'http://localhost/api/job'
                octoprint_api_key = self._settings.get(["apiKey"])
       
                assert octoprint_api_key is not None and len(octoprint_api_key) > 0

                response = requests.get(job_uri,  headers = { "X-Api-Key" : octoprint_api_key }, timeout=HTTP_REQUEST_TIMEOUT)
                response.raise_for_status()

                return response.json()

        def _get_slice_profile(self, slicer, slice_profile_name):
                profile_uri = "http://localhost/api/slicing/{}/profiles/{}".format(slicer, slice_profile_name)
                octoprint_api_key = self._settings.get(["apiKey"])

                assert octoprint_api_key is not None and len(octoprint_api_key) > 0

                response = requests.get(profile_uri,  headers = { "X-Api-Key" : octoprint_api_key }, timeout=HTTP_REQUEST_TIMEOUT)
                response.raise_for_status()

                return response.json()

        def _get_printer_profile(self, printer_profile_id):
                profile_uri = "http://localhost/api/printerprofiles"
                octoprint_api_key = self._settings.get(["apiKey"])

                assert octoprint_api_key is not None and len(octoprint_api_key) > 0

                response = requests.get(profile_uri,  headers = { "X-Api-Key" : octoprint_api_key }, timeout=HTTP_REQUEST_TIMEOUT)
                response.raise_for_status()
                json_response = response.json()

                print('P' * 40 + str(printer_profile_id))

                return json_response['profiles'][printer_profile_id]

        def _get_current_printer_profile(self):
                profile_uri = "http://localhost/api/printerprofiles"
                octoprint_api_key = self._settings.get(["apiKey"])

                assert octoprint_api_key is not None and len(octoprint_api_key) > 0

                response = requests.get(profile_uri,  headers = { "X-Api-Key" : octoprint_api_key }, timeout=HTTP_REQUEST_TIMEOUT)
                response.raise_for_status()
                printers = response.json()['profiles']

                for printer in printers:
                        if printers[printer]['current']:
                                return printers[printer]

        def _get_default_slice_profile(self, slicer):
                profile_uri = "http://localhost/api/slicing/{}/profiles".format(slicer)
                octoprint_api_key = self._settings.get(["apiKey"])

                assert octoprint_api_key is not None and len(octoprint_api_key) > 0

                response = requests.get(profile_uri,  headers = { "X-Api-Key" : octoprint_api_key }, timeout=HTTP_REQUEST_TIMEOUT)
                response.raise_for_status()
                profiles = response.json()

                for profile in profiles:
                        if profiles[profile]['default']:
                                return profile

        def _get_local_file_metadata(self, local_file_name):
                local_file_uri = "http://localhost/api/files/local/{}".format(urllib.quote_plus(local_file_name))
                octoprint_api_key = self._settings.get(["apiKey"])

                assert octoprint_api_key is not None and len(octoprint_api_key) > 0

                response = requests.get(local_file_uri,  headers = { "X-Api-Key" : octoprint_api_key }, timeout=HTTP_REQUEST_TIMEOUT)
                response.raise_for_status()
                json_response = response.json()

                return json_response

        def _get_current_job(self):
                job_uri = "http://localhost/api/job"
                octoprint_api_key = self._settings.get(["apiKey"])

                assert octoprint_api_key is not None and len(octoprint_api_key) > 0

                response = requests.get(job_uri,  headers = { "X-Api-Key" : octoprint_api_key }, timeout=HTTP_REQUEST_TIMEOUT)
                response.raise_for_status()
                job = response.json()

                return job

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

                        internal_progress = current_spool_settings.get('jobProgress')

                        if internal_progress != '':
                                internal_progress = float(internal_progress) 

                        if job_completion_percent is not None:
                                
                                # If a job reset has been detected, set initial length to length
                                if internal_progress != '' and internal_progress > job_completion_percent:
                                        initial_length = float(current_spool_settings['length'])
					current_spool_settings['initial_length'] = str(current_spool_settings['length'])   

                                # Job filament length is in millimeters, so must convert to meters
                                length_job_used = (job_completion_percent / 100) * (estimated_job_length / 1000)

                                new_length = initial_length - length_job_used

                                current_spool_settings['length'] = new_length

                                current_spool_settings['length'] = str(current_spool_settings['length'])
 
                                current_spool_settings['jobProgress'] = job_completion_percent

                                octoprint.plugin.SettingsPlugin.on_settings_save(self, current_spool_settings)
                        # If a job reset has been detected, set initial length to length
                        elif job_completion_percent is None and internal_progress != '':
                                current_spool_settings['initial_length'] = str(current_spool_settings['length'])
                                current_spool_settings['jobProgress'] = ''
                                octoprint.plugin.SettingsPlugin.on_settings_save(self, current_spool_settings)

                        if update_remote:
                                current_spool_settings['length'] = float(current_spool_settings['length'])
                                self._post_spool_data(current_spool_settings)
                except Exception as e:
                        self._logger.error("Could not update length: {}".format(str(e)))

        def _set_default_slice_profile(self, muid_prefix):
                slice_profile_path = settings().get(['folder', 'slicingProfiles'])
                
                slice_manager = SlicingManager(slice_profile_path, printerProfileManager)
                slice_manager.reload_slicers()
                default_slicer = slice_manager.default_slicer
                slice_manager.set_default_profile(default_slicer, muid_prefix, require_exists=True)
                

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

                subprocess_args.append('-u')

                current_url = request.url
                split_url = urlsplit(current_url)

                split_url_port = ''
                
                if split_url.port is not None:
                        split_url_port = ":{}".format(split_url.port) 

                subprocess_args.append("{}://{}{}".format(split_url.scheme, split_url.hostname, split_url_port))

                print('#' * 50 + str(subprocess_args)) 
                
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
                                               octoprint.plugin.SettingsPlugin.on_settings_save(self, {'printProgress': ''})
                                       else:
                                               self._post_spool_data(return_result)

                               except Exception as e:
                                       return flask.jsonify(result=return_result, locbit_error=str(e))

                               try:
                                       self._set_default_slice_profile(return_result['muid'][0:7])
                               except Exception as e:
                                       return flask.jsonify(result=return_result, locbit_error="Setting profile {} as default failed, check to see if it exists".format(return_result['muid']))

                               return_result['length'] = "{0:.3f}".format(float(return_result['length'])) 

		               return flask.jsonify(result=return_result)
		       else:
		               return flask.jsonify(error="Invalid QR code")

        def _update_profile_event_stats(self, printer_event):

                sharing_mode = self._settings.get(['sharingMode'])
                
                if not sharing_mode:
                        self._logger.info('Sharing Mode turned off, skipping profile stat update')
                        return

                current_printer = self._get_current_printer_profile()

                printer_make = current_printer['id']
                printer_model = current_printer['model']
                nozzle_size = current_printer['extruder']['nozzleDiameter']

                muid = self._settings.get(['muid'])[0:7]

                current_job = self._get_current_job()

                gcode_file_name = current_job['job']['file']['name']
                gcode_file_metadata = self._get_local_file_metadata(gcode_file_name)
                gcode_identifier = gcode_file_metadata['hash']

                layer_height = None
                
                try:
                        layer_height = int( self._settings.get(['layerHeight']) )
                        assert layer_height > 0
                except Exception as e:
                        self._logger.error('Cannot make profile stat request, layer height must be non-zero positive integer')
                        return

                profile_update_data =json.dumps( {
                                                  'printer_event': printer_event, 
                                                  'muid': muid,
                                                  'gcode_identifier': gcode_identifier,
                                                  'printer_make': printer_make,
                                                  'printer_model': printer_model,
                                                  'nozzle_size': nozzle_size, 
                                                  'layer_height': layer_height
                                                 }
                                               )  
                
                self._logger.info('UPDATE' * 5 + str(profile_update_data))
                
                locbit_info_share_event_uri = 'https://sd3d.locbit.com/event' 

                locbit_api_key = self._settings.get(['locbitAPIKey'])
                locbit_access_id = self._settings.get(['locbitAccessID'])

                if len(locbit_api_key) == 0 or len(locbit_access_id) == 0:
                        self._logger.error("No API key or access key in settings. Skipping stat update")
                        return

                query_params = {'api': locbit_api_key, 'access': locbit_access_id}

                response = requests.post(locbit_info_share_event_uri, params=query_params, headers={'Content-Type': 'application/json'}, data=profile_update_data).json()

                self._logger.info('EVENT STAT RESPONSE' * 3 + str(response)) 

        def _associate_profile_gcode(self, gcode_identifier, slicer, slicing_profile_name, printer_profile_id):

                self._logger.info('ASSOCIATE PROFILE' * 4 + slicing_profile_name)

                slicing_profile = self._get_slice_profile(slicer, slicing_profile_name)

                printer_profile = {}

                if isinstance(printer_profile_id, dict):
                        printer_profile = printer_profile_id
                else:
                        printer_profile = self._get_printer_profile(printer_profile_id)

                layer_height = None

                try:
                        layer_height = int( self._settings.get(['layerHeight']) )
                        assert layer_height > 0
                except Exception as e:
                        self._logger.error('Cannot make gcode association request, layer height must be non-zero positive integer')
                        return

                request_data = json.dumps({'muid': self._settings.get(['muid'])[0:7], 'gcode_identifier': gcode_identifier, 
                                           'slicing_profile': slicing_profile, 'printer_make': printer_profile_id,
                                           'printer_model': printer_profile['model'], 'nozzle_size': printer_profile['extruder']['nozzleDiameter'], 'layer_height': layer_height})
 
                self._logger.info('PROFILE ASSOCIATION REQUEST' * 3 + str(request_data))

                locbit_info_share_uri = 'https://sd3d.locbit.com/profile'

                locbit_api_key = self._settings.get(['locbitAPIKey'])
                locbit_access_id = self._settings.get(['locbitAccessID'])

                if len(locbit_api_key) == 0 or len(locbit_access_id) == 0:
                        self._logger.error("No API key or access key in settings. Skipping profile update")
                        return

                query_params = {'api': locbit_api_key, 'access': locbit_access_id}

                response = requests.post(locbit_info_share_uri, params=query_params, headers={'Content-Type': 'application/json'}, data=request_data).json()

                self._logger.info('PROFILE ASSOCIATION RESPONSE' * 3 + str(response))
                
                 

	def on_after_startup(self):
		self._logger.info("Hello world! I am: %s" % self._settings.get(["did"]))
                
                def slice_monkey_patch_gen(slice_func):
                        def slice_monkey_patch(*args, **kwargs):

                                original_callback = args[5]

                                def patched_callback(*callbackargs, **callbackkwargs):

                                        if 'callback_args' in kwargs and 'callback_kwargs' in kwargs:
                                                original_callback(*kwargs['callback_args'], **kwargs['callback_kwargs'])
                                        elif 'callback_args' in kwargs and 'callback_kwargs' not in kwargs:

                                                gco_file = None

                                                for arg in kwargs['callback_args']:
                                                        if arg.endswith('gco') and arg != args[3]:
                                                                gco_file = arg
                                                                break

                                                original_callback(*kwargs['callback_args'])

                                                if gco_file is not None:
                                                        gco_hash = self._get_local_file_metadata(gco_file)['hash']

                                                        self._associate_profile_gcode(gco_hash, args[1], args[4], kwargs['printer_profile_id'])
                                                
                                                
                                        elif 'callback_args' not in kwargs and 'callback_kwargs' in kwargs:
                                                original_callback(*kwargs['callback_kwargs'])
                                        elif 'callback_args' not in kwargs and 'callback_kwargs' not in kwargs:
                                                original_callback() 
                              
                                sharing_mode = self._settings.get(['sharingMode']) 
                                
                                if sharing_mode:
                                        arg_list = list(args)
                                        arg_list[5] = patched_callback
                                        args = tuple(arg_list)
                                
                                slice_func(*args, **kwargs)

                        return slice_monkey_patch

                octoprint.slicing.SlicingManager.slice = slice_monkey_patch_gen(octoprint.slicing.SlicingManager.slice)

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
                            camFlipHorizontal=False,
                            jobProgress='',
                            layerHeight='',
                            sharingMode=False,
                            autoPrintMode=False)

	def get_template_configs(self):
		return [
			dict(type="navbar", custom_bindings=False),
			dict(type="settings", custom_bindings=False)
		]

	def get_assets(self):
		return dict(js=["js/Locbit.js"])

        def _auto_print(self, file_info):

                if not self._settings.get(['autoPrintMode']):
                        return

                file_name = file_info['name']
                file_path = file_info['path']
                file_target = file_info['target']

                if file_name.endswith('.stl') and file_target == 'local':
                        auto_print_uri = "http://localhost/api/files/local/{}".format(urllib.quote_plus(file_path))
                        octoprint_api_key = self._settings.get(["apiKey"])

                        default_slice_profile = self._get_default_slice_profile('cura')
                        printer_profile = self._get_current_printer_profile()
                        
                        slice_data = {
                                      'command': 'slice',
                                      'print': True,
                                      'profile': default_slice_profile,
                                      'printerProfile': printer_profile
                                     }

                        assert octoprint_api_key is not None and len(octoprint_api_key) > 0
                        response = requests.post(auto_print_uri, headers = { "X-Api-Key" : octoprint_api_key }, json=slice_data, timeout=HTTP_REQUEST_TIMEOUT)
                        response.raise_for_status()
                        json_response = response.json()

                        return json_response
   

	def on_event(self, event, payload, **kwargs):
		global Layer
		global uid
		global url
		did = self._settings.get(["did"])

		self.checkPrinterStatus()

		if event == "PrintStarted":
			Layer = 0
			self.sendLayerStatus(Layer)
                        self._update_spool_length(update_remote=True)
                        self._update_profile_event_stats(event) 
		elif event == "PrintFailed":
			Layer = 0
			self.sendLayerStatus(Layer)
                        self._update_spool_length(update_remote=True)
                        self._update_profile_event_stats(event)
		elif event == "PrintCancelled":
			Layer = 0
			self.sendLayerStatus(Layer)
                        self._update_spool_length(update_remote=True)
                        self._update_profile_event_stats(event)
                elif event == "PrintDone":
                        self._update_spool_length(update_remote=True)
                        self._update_profile_event_stats(event) 
                elif event == "PrintPaused":
                        self._update_spool_length(update_remote=True)
                        self._update_profile_event_stats(event)
                elif event == "PrintResumed":
                        self._update_profile_event_stats(event)
                elif event == "Upload":
                        self._auto_print(payload)
                        
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
