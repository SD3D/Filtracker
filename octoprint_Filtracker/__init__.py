from __future__ import absolute_import, division
from httplib import BadStatusLine
from .FiltrackerNotifications import FiltrackerMsgDict, FiltrackerPrintingStatusDict, FiltrackerPrinterStatusDict, FiltrackerSlicingStatusDict

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
url = "http://0.0.0.0:8001/event"
status_url = 'https://api.locbit.com/statusByLid'

HTTP_REQUEST_TIMEOUT=50
LAYER_HEIGHT_THRESHOLD=0.1

class FiltrackerPlugin(octoprint.plugin.StartupPlugin,
                        octoprint.plugin.BlueprintPlugin,
			octoprint.plugin.TemplatePlugin,
			octoprint.plugin.SettingsPlugin,
			octoprint.plugin.EventHandlerPlugin,
			octoprint.plugin.AssetPlugin,
			octoprint.plugin.SimpleApiPlugin,
                        octoprint.plugin.WizardPlugin):


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

        #_post_spool_data
        #overrrides the current length of the spool on the server,
        #self, spool_data
        def _post_spool_data(self, spool_data):
                self._send_printer_status() 
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

        #_get_spool_length
        #grabs the current length of the spool.
        #self, muid
        def _get_spool_length(self, muid):

                SD3D_api_key = self._settings.get(['SD3DAPIKey'])
                SD3D_access_id = self._settings.get(['SD3DAccessID'])

                if len(SD3D_api_key) == 0 or len(SD3D_access_id) == 0:
                        raise Exception("Cannot get stored spool length, either Filtracker api key or access ID is missing from settings")

                request_uri = "{}/{}/SD3DPrinter".format(status_url, muid)

                query_params = {'api': SD3D_api_key, 'access': SD3D_access_id} 

                response = requests.get(request_uri, params=query_params, timeout=HTTP_REQUEST_TIMEOUT)

                response.raise_for_status()

                response_data = response.json()

                if 'measurements' in response_data and 'Length' in response_data['measurements']:
                        length = response_data['measurements']['Length'].get('status')
                        return length
                elif 'success' in response_data and \
                      not response_data['success'] and \
                      response_data['message'] == 'Device is not found':
                        return None
                else:
                      return None

        #_get_spool_settings
        #grabs the current spool data from the settings. Color, muid, material, length, initial_length, jobprogress
        #settings dict
        def _get_spool_settings(self):

                setting_keys = ['muid', 'material', 'color', 'diameter', 'length', 'initial_length', 'jobProgress']

                setting_dict = {}

                for setting_key in setting_keys:

                        setting_value = self._settings.get([setting_key])

                        setting_dict[setting_key] = setting_value

                return setting_dict 

        #_get_printer_job_info
        #checks the localhost for information on the current job. 
        #self
        #response.json
        def _get_printer_job_info(self):
                job_uri = 'http://localhost/api/job'
                octoprint_api_key = settings().get(['api', 'key']) 
       
                assert octoprint_api_key is not None and len(octoprint_api_key) > 0

                response = requests.get(job_uri,  headers = { "X-Api-Key" : octoprint_api_key }, timeout=HTTP_REQUEST_TIMEOUT)
                response.raise_for_status()

                return response.json()

        #_get_slice_profile
        #retrieves the slicing profile.
        #self, slicer, slice_profile_name
        #response.json
        def _get_slice_profile(self, slicer, slice_profile_name):
                profile_uri = "http://localhost/api/slicing/{}/profiles/{}".format(slicer, slice_profile_name)
                octoprint_api_key = settings().get(['api', 'key']) 

                assert octoprint_api_key is not None and len(octoprint_api_key) > 0

                response = requests.get(profile_uri,  headers = { "X-Api-Key" : octoprint_api_key }, timeout=HTTP_REQUEST_TIMEOUT)
                response.raise_for_status()

                return response.json()

        #_get_printer_profile
        #retrieves the current printer profile. 
        #self, printer_profile_id
        #json_response['profiles'][printer_profile_id]
        def _get_printer_profile(self, printer_profile_id):
                profile_uri = "http://localhost/api/printerprofiles"
                octoprint_api_key = settings().get(['api', 'key']) 

                assert octoprint_api_key is not None and len(octoprint_api_key) > 0

                response = requests.get(profile_uri,  headers = { "X-Api-Key" : octoprint_api_key }, timeout=HTTP_REQUEST_TIMEOUT)
                response.raise_for_status()
                json_response = response.json()

                return json_response['profiles'][printer_profile_id]

        #_get_current_printer_profile
        #grabs the current profile from the localhost.
        #self
        def _get_current_printer_profile(self):
                profile_uri = "http://localhost/api/printerprofiles"
                octoprint_api_key = settings().get(['api', 'key']) 

                assert octoprint_api_key is not None and len(octoprint_api_key) > 0

                response = requests.get(profile_uri,  headers = { "X-Api-Key" : octoprint_api_key }, timeout=HTTP_REQUEST_TIMEOUT)
                response.raise_for_status()
                printers = response.json()['profiles']

                for printer in printers:
                        if printers[printer]['current']:
                                return printers[printer]

        #_get_default_slice_profile
        #grabs the default slicing profile
        #self, slicer
        def _get_default_slice_profile(self, slicer):
                profile_uri = "http://localhost/api/slicing/{}/profiles".format(slicer)
                octoprint_api_key = settings().get(['api', 'key']) 

                assert octoprint_api_key is not None and len(octoprint_api_key) > 0

                response = requests.get(profile_uri,  headers = { "X-Api-Key" : octoprint_api_key }, timeout=HTTP_REQUEST_TIMEOUT)
                response.raise_for_status()
                profiles = response.json()

                for profile in profiles:
                        if profiles[profile]['default']:
                                return profile

        #_get_local_file_metadata
        #gathers metadata from the local host
        #self, local_file_name
        def _get_local_file_metadata(self, local_file_name):
                local_file_uri = "http://localhost/api/files/local/{}".format(urllib.quote_plus(local_file_name))
                octoprint_api_key = settings().get(['api', 'key']) 

                assert octoprint_api_key is not None and len(octoprint_api_key) > 0

                response = requests.get(local_file_uri,  headers = { "X-Api-Key" : octoprint_api_key }, timeout=HTTP_REQUEST_TIMEOUT)
                response.raise_for_status()
                json_response = response.json()

                return json_response

        #_get_current_job
        #get the current job info from the localhost
        #self
        def _get_current_job(self):
                job_uri = "http://localhost/api/job"
                octoprint_api_key = settings().get(['api', 'key']) 

                assert octoprint_api_key is not None and len(octoprint_api_key) > 0

                response = requests.get(job_uri,  headers = { "X-Api-Key" : octoprint_api_key }, timeout=HTTP_REQUEST_TIMEOUT)
                response.raise_for_status()
                job = response.json()

                return job

        #_update_spool_length
        #Alters the spool length throghout the different events.
        #self, update_remote=False
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
                                length_job_used = (job_completion_percent / 100) * (float(estimated_job_length) / 1000)

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

        #_set_default_slice_profile
        #sets the definitions for the slicing variables.
        #self, profile_name
        def _set_default_slice_profile(self, profile_name):
                slice_profile_path = settings().get(['folder', 'slicingProfiles'])
                
                slice_manager = SlicingManager(slice_profile_path, printerProfileManager)
                slice_manager.reload_slicers()
                default_slicer = slice_manager.default_slicer
                slice_manager.set_default_profile(default_slicer, profile_name, require_exists=True)
                
        #on_api_get
        #Creates triggers for install, settings, and auto-print. Then gives permission and executes the qr reader.
        #self, request
	def on_api_get(self, request):

                if request.args.get('install') == '1':
                        try:
                                fill_percent = request.args.get('fill')
                                
                                self.install_dependencies(fill_percent)
                                return flask.jsonify(result='')
                        except Exception as e:
                                return flask.jsonify(error=str(e)) 
                if request.args.get('settings') == '1':
                        
                        return_result = {}                 
                        
                        for qr_data_key in ['material', 'diameter', 'color', 'length', 'muid']:
                                return_result[qr_data_key] = self._settings.get([qr_data_key])
                       
                        try:
                                return_result['length'] = "{0:.3f}".format(float(return_result['length']))
                        except Exception as e:
                                self._logger.info('Could not return length')
                                
                        return flask.jsonify(result=return_result)

                if request.args.get('autoprint_setting') == '1':
                        return flask.jsonify(result=self._settings.get(['autoPrintMode']))
                
		# grant permission to the file before execute it
		commands = ['/bin/chmod +x /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/qr.py']
		import subprocess
		for command in commands:
                        subprocess.check_call("/bin/bash -c 'sudo {}'".format(command), shell=True)

                qr_script_path = '/home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/qr.py'
                subprocess_args = [qr_script_path]

                output = ''
                
                subprocess_args.append('-u')

                current_url = request.url
                split_url = urlsplit(current_url)

                split_url_port = ''
                
                if split_url.port is not None:
                        split_url_port = ":{}".format(split_url.port) 

                subprocess_args.append("{}://{}{}".format(split_url.scheme, split_url.hostname, split_url_port))

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
                                       return flask.jsonify(result=return_result, Filtracker_error=str(e))

                               try:
                                       self._set_default_slice_profile(return_result['muid'][0:7])

                               except Exception as e:
                                       return flask.jsonify(result=return_result, Filtracker_error="Setting profile {} as default failed, check to see if it exists".format(return_result['muid']))

                               return_result['length'] = "{0:.3f}".format(float(return_result['length']))

		               return flask.jsonify(result=return_result)
		       else:
		               return flask.jsonify(error="Invalid QR code")

        #_update_profile_event_stats
        #when events happen, this changes them stats and sends them to the cloud profile.
        #self, printer_event
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

                #layer_height = None
                
                #try:
                #        layer_height = int( self._settings.get(['layerHeight']) )
                #        assert layer_height > 0
                #except Exception as e:
                #        self._logger.error('Cannot make profile stat request, layer height must be non-zero positive integer')
                #        return
                tmp_json = {
                        'printer_event': printer_event,
                        'muid': muid,
                        'gcode_identifier': gcode_identifier,
                        'printer_make': printer_make,
                        'printer_model': printer_model,
                        'nozzle_size': nozzle_size
                }
                if len(str(self._settings.get(['diameter']))) > 0:
                        tmp_json["diameter"] = float("{0:.3f}".format(float(self._settings.get(['diameter']))))
                profile_update_data =json.dumps(tmp_json)
                self._logger.info('WORKING UPDATE' * 5 + str(profile_update_data))
                
                Filtracker_info_share_event_uri = 'https://sd3d.locbit.com/event' 

                SD3D_api_key = self._settings.get(['SD3DAPIKey'])
                SD3D_access_id = self._settings.get(['SD3DAccessID'])

                if len(SD3D_api_key) == 0 or len(SD3D_access_id) == 0:
                        self._logger.error("No API key or access key in settings. Skipping stat update")
                        return

                query_params = {'api': SD3D_api_key, 'access': SD3D_access_id}

                response = requests.post(Filtracker_info_share_event_uri, params=query_params, headers={'Content-Type': 'application/json'}, data=profile_update_data).json()

                self._logger.info('EVENT STAT RESPONSE' * 3 + str(response))
                # TODO: check if response has the key called data 
                if printer_event == 'PrintStarted' and not response['success']:
                        self._logger.error("Profile stats update failed: %s".format(response['data']))
                        self._send_client_alert("Could not update profile stats on PrintStart: %s" % response['data'])
               
        #_download_best_profile
        #if cloud mode is active, it will downoad the best profil available. 
        #self
        def _download_best_profile(self):

                cloud_mode = self._settings.get(['cloudMode'])

                if not cloud_mode:
                        self._logger.info('Cloud Mode turned off, skipping best profile download')
                        return        

                current_printer = self._get_current_printer_profile()

                printer_make = current_printer['id']
                printer_model = current_printer['model']
                nozzle_size = current_printer['extruder']['nozzleDiameter']

                muid = self._settings.get(['muid'])[0:7]

                material_diameter = float("{0:.3f}".format(float(self._settings.get(['diameter']))))

                layer_height = None
                layer_height_threshold = LAYER_HEIGHT_THRESHOLD 

                try:
                        layer_height = float(self._settings.get(['layerHeight']))
                except Exception as e:
                        self._logger.error("Could not parse layer height {}, skipping best profile download".format(layer_height))
                        return

                best_profile = self._get_best_profile(printer_make, printer_model, nozzle_size, muid, layer_height, layer_height_threshold, material_diameter)

                if best_profile['success']:
                        print("best profile data:" + str(best_profile))
                        best_profile['data']['slicing_profile']['key'] = 'Filtracker' + best_profile['data']['slicing_profile']['key']

                        best_profile['data']['slicing_profile']['default'] = False

                        self._upload_new_profile(best_profile['data']['slicing_profile'])

                        self._set_best_or_default_profile(best_profile['data']['slicing_profile']['key'])
                else:
                        self._logger.error("Error getting best profile, skipping best profile download")
                        muid_prefix = self._settings.get(['muid'])[0:7]
                        try:
                                self._set_default_slice_profile(muid_prefix)
                        except Exception as e:
                                self._logger.error("Could not set default muid profile %s".format(muid_prefix))
                                self._send_client_alert("Could not get best profile and setting default slice profile for muid %s failed" % muid_prefix)

        def _send_client_alert(self, message):
                self._plugin_manager.send_plugin_message(self._identifier, message)

        #_set_best_or_default_profiles
        #chooses the best profile, or chooese the default.
        #self, best_profile_name
        def _set_best_or_default_profile(self, best_profile_name):
                
                muid_prefix = self._settings.get(['muid'])[0:7]
                
                try:
                        self._set_default_slice_profile(best_profile_name)
                except Exception as e:

                        try:
                                self._set_default_slice_profile(muid_prefix)
                        except Exception as e:
                                self._logger.error("Could not set best profile %s, nor default muid profile %s, check if either one exists".format(best_profile_name, muid_prefix))
                                self._send_client_alert("Could not set best profile %s, nor default muid profile %s, check if either one exists" % (best_profile_name, muid_prefix)) 

        #_get_best_profile
        #Compares the best cloud profiles based off comlpetion percentage.
        #self, printer_make, printer_model, nozzle_size, muid, layer_height, layer_height_threshold, material_diameter
        #response.json
        def _get_best_profile(self, printer_make, printer_model, nozzle_size, muid, layer_height, layer_height_threshold, material_diameter):
                #printer_make = urllib.quote(printer_make)
                #printer_model = urllib.quote(printer_model)

                SD3D_api_key = self._settings.get(['SD3DAPIKey'])
                SD3D_access_id = self._settings.get(['SD3DAccessID'])

                query_data = {
                              'printer_make': printer_make,
                              'printer_model': printer_model,
                              'nozzle_size': nozzle_size,
                              'muid': muid,
                              'layer_height': layer_height,
                              'layer_height_threshold': layer_height_threshold,
                              'material_diameter': material_diameter,
                              'api': SD3D_api_key,
                              'access': SD3D_access_id
                             }

                query_str = urllib.urlencode(query_data)

                if len(SD3D_api_key) == 0 or len(SD3D_access_id) == 0:
                       self._logger.error("No API key or access key in settings. Skipping getting best profile")
                       return 

                Filtracker_uri = 'https://sd3d.locbit.com/slicing_profile'

                self._logger.info('GET BEST PROFILE REQUEST' * 3 + str(query_data))

                response = requests.get(Filtracker_uri, params=query_data)

                self._logger.info('GET BEST PROFILE RESPONSE' * 3 + str(response.json()) + str(response.url))

                return response.json()
        
        #_upload_new_profile
        #Uploads a profile frfom local to the cloud.
        #self, profile
        #response.json() --> json object that conrains the profile uri and the api-key.
        def _upload_new_profile(self, profile):
                profile_uri = "http://localhost/api/slicing/cura/profiles/{}".format(profile['key'])
                octoprint_api_key = settings().get(['api', 'key']) 

                assert octoprint_api_key is not None and len(octoprint_api_key) > 0

                response = requests.put(profile_uri,  headers = { "X-Api-Key" : octoprint_api_key}, json=profile, timeout=HTTP_REQUEST_TIMEOUT)
                response.raise_for_status()

                return response.json()
                  
        #_associate_profile_gcode
        #Adds athe proper files to the right profiles. 
        #self, gcode_indentifier, slicer, slicing_profile_name, printer_profile_id
        def _associate_profile_gcode(self, gcode_identifier, slicer, slicing_profile_name, printer_profile_id):

                self._logger.info('ASSOCIATE PROFILE' * 4 + slicing_profile_name)

                slicing_profile = self._get_slice_profile(slicer, slicing_profile_name)

                printer_profile = {}

                printer_profile = self._get_printer_profile(printer_profile_id)

                #layer_height = None

                #try:
                #        layer_height = int( self._settings.get(['layerHeight']) )
                #        assert layer_height > 0
                #except Exception as e:
                #        self._logger.error('Cannot make gcode association request, layer height must be non-zero positive integer')
                #        return

                request_data = json.dumps({'muid': self._settings.get(['muid'])[0:7], 'gcode_identifier': gcode_identifier, 
                                           'slicing_profile': slicing_profile, 'printer_make': printer_profile_id,
                                           'printer_model': printer_profile['model'], 'nozzle_size': printer_profile['extruder']['nozzleDiameter'],
                                           'material_diameter': float("{0:.3f}".format(float(self._settings.get(['diameter'])))) }) 
                                           #'layer_height': layer_height})
 
                self._logger.info('PROFILE ASSOCIATION REQUEST' * 3 + str(request_data))

                Filtracker_info_share_uri = 'https://sd3d.locbit.com/profile'

                SD3D_api_key = self._settings.get(['SD3DAPIKey'])
                SD3D_access_id = self._settings.get(['SD3DAccessID'])

                if len(SD3D_api_key) == 0 or len(SD3D_access_id) == 0:
                        self._logger.error("No API key or access key in settings. Skipping profile update")
                        return

                query_params = {'api': SD3D_api_key, 'access': SD3D_access_id}

                response = requests.post(Filtracker_info_share_uri, params=query_params, headers={'Content-Type': 'application/json'}, data=request_data).json()

                self._logger.info('PROFILE ASSOCIATION RESPONSE' * 3 + str(response))

        #_auto_provision_printer
        #Automatically provisions a printer to the locbit platform.
        #self
        def _auto_provision_printer(self):
                from uuid import getnode as get_mac
                SD3D_api_key = self._settings.get(['SD3DAPIKey'])
                SD3D_access_id = self._settings.get(['SD3DAccessID'])

                query_params = {'api': SD3D_api_key, 'access': SD3D_access_id}
                did = self._settings.get(['did'])
                lid = get_mac()
		printer_oem = self._get_current_printer_profile()['name']
		printer_model = self._get_current_printer_profile()['model']
		pretxt = 'Printer: '
		posttxt = '('
		closetxt = ')'
		printer_dname = "%s %s %s %s %s %s" % (pretxt, printer_oem, printer_model, posttxt, lid, closetxt)

                provision_post_data = json.dumps({
                                                  'translator': 'SD3DPrinter',
                                                  'DeviceName': printer_dname,
                                                  'lid': lid,
                                                  'deviceDescriptionId': '56db96454a7a901f59815541',
                                                  'locationId': '13',
                                                  'userId': '116'})

                self._logger.info('PRINTER AUTO PROVISION REQUEST' * 3 + str(provision_post_data))

                response = requests.post('https://api.locbit.com/provision', params=query_params, headers={'Content-Type': 'application/json'}, data=provision_post_data).json()

                self._logger.info('PRINTER AUTO PROVISION RESPONSE' * 3 + str(response))

                if 'success' in response and response['success']:

                        provision_did = response['message']['did']

                        activation_post_data = json.dumps({'did': provision_did,
                                                           'connectivity': True,
                                                           'services': True
                                                          })
                        
                        self._logger.info('PRINTER ACTIVATION REQUEST' * 3 + str(activation_post_data))

                        activate_response = requests.post('https://billing.locbit.com/charge', params=query_params, headers={'Content-Type': 'application/json'}, data=activation_post_data).json()

                        self._logger.info('PRINTER ACTIVATION RESPONSE' * 3 + str(activate_response))

        #install_dependencies
        #If a printer is installing the plugin for the first time, this is a series of commands to setup up the plugin automatically. 
        #self, fill_density
        def install_dependencies(self, fill_density):
                import subprocess, sys, os
                from uuid import getnode as get_mac
                settings().set(['folder', 'slicingProfiles'], '/home/pi/.octoprint/slicingProfiles')
                settings().set(['slicing', 'defaultSlicer'], 'cura', force=True)
                octoprint.plugin.SettingsPlugin.on_settings_save(self, {'macAddress': get_mac()})


                try:
                        fill_density_percentage = int(fill_density)
                        assert fill_density_percentage > 0 and fill_density_percentage <= 100
                        octoprint.plugin.SettingsPlugin.on_settings_save(self, {'fillDensity': fill_density})
                except Exception as e:
                        raise Exception("Fill density setting {} is invalid, must be percentage (integer)".format(fill_density))

                commands = [
                            '/usr/bin/apt-get update',
                            '/usr/bin/apt-get install -y ipython python-opencv python-scipy python-numpy python-setuptools python-pip python-pygame python-zbar',
                            '/bin/chmod +x /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/qr.py',
                            '/usr/bin/pip install --upgrade pip',
                            '/usr/local/bin/pip --no-cache-dir install timeout-decorator svgwrite https://github.com/sightmachine/SimpleCV/zipball/master',
                            '/bin/mv /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/edge_set.py /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/edge_set.sh',
                            '/bin/chmod 755 ~/oprint/lib/python2.7/site-packages/octoprint_Filtracker/edge_set.sh',
                            '/home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/edge_set.sh',
                            '/bin/mv /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/zip_check.py /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/zip_check.sh',
                            '/bin/chmod 755 ~/oprint/lib/python2.7/site-packages/octoprint_Filtracker/zip_check.sh',
                            '/home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/zip_check.sh',
                            '/usr/bin/wget -P ~/oprint/lib/python2.7/site-packages/octoprint_Filtracker https://github.com/Locbit/locbit-edge/archive/master.zip',
                            '/usr/bin/unzip ~/oprint/lib/python2.7/site-packages/octoprint_Filtracker/master.zip -d ~/oprint/lib/python2.7/site-packages/octoprint_Filtracker',
                            '/bin/mv /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/locbit-edge-master/config.js.default /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/locbit-edge-master/config.js',
                            '/bin/mv /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/shell.py /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/locbit-edge-master/shell.sh',
                            '/bin/chmod 755 ~/oprint/lib/python2.7/site-packages/octoprint_Filtracker/locbit-edge-master/shell.sh',
                            '/home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/locbit-edge-master/shell.sh',
                            '/bin/cp /home/pi/oprint/lib/python2.7/site-packages/octoprint_Filtracker/pm_check.py /etc/init.d/pm_check.sh',
                            '/bin/chmod 755 /etc/init.d/pm_check.sh',
                            'update-rc.d pm_check.sh defaults'
                        ]
                for command in commands:
                        subprocess.check_call("/bin/bash -c 'sudo {}'".format(command), shell=True)
        #on_after_startup
        #A series of commands and instructions to execute after the server starts up.
        #self
        #slice monkey patch
	def on_after_startup(self):
                from uuid import getnode as get_mac
                self._logger.info("MAC: {}".format(get_mac()))
                current_printer_name = self._get_current_printer_profile()['id']
                octoprint.plugin.SettingsPlugin.on_settings_save(self, {'did': current_printer_name})

		current_printer_oem = self._get_current_printer_profile()['name']
                octoprint.plugin.SettingsPlugin.on_settings_save(self, {'oem': current_printer_oem})
		
		current_printer_model = self._get_current_printer_profile()['model']
                octoprint.plugin.SettingsPlugin.on_settings_save(self, {'model': current_printer_model})

		self._logger.info("Hello world! I am: %s" % self._settings.get(["did"]))

                self._auto_provision_printer()

                self._send_printer_status_with_timer() 

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
                self._send_printer_status_with_timer()
        #get_settins_def
        #Declares the settings variables 
        #self
	def get_settings_defaults(self):
		return dict(did='',
			    oem='',
			    model='',
                            material='',
                            diameter='',
                            color='',
                            initial_length='',
                            length='',
                            muid='',
                            SD3DAPIKey='yCX9PgjsvzGuaKTT9yuUIJFehPHjMknU',
                            SD3DAccessID='DxM7QlAsDo43Z0SJW1qwLh4FBXGQlaGU',
                            jobProgress='',
                            layerHeight='0.25',
                            sharingMode=True,
                            cloudMode=True,
                            autoPrintMode=True,
                            macAddress='',
                            fillDensity='20',
                            updateInterval= 300,
                            PrintingStatus= 'Unknown',
                            PrinterStatus= 'Unknown',
                            SlicingStatus= 'Unknown'
                            )

	def get_template_configs(self):
		return [
			dict(type="navbar", custom_bindings=False),
			dict(type="settings", custom_bindings=False)
		]

	def get_assets(self):
		return dict(js=["js/Filtracker.js"])

        #_auto_print
        #Exclusive to the "upload" event. Automatically slices stl --> GCODE and starts printing.
        #self, file_info --> data from the uploaded file that will be printed.
        #JSON respones
        def _auto_print(self, file_info):
                global did
                global uid

                if not self._settings.get(['autoPrintMode']):
                        return

                fill_density_percentage = self._settings.get(['fillDensity'])

                try:
                        fill_density_percentage = int(fill_density_percentage)
                        assert fill_density_percentage > 0 and fill_density_percentage <= 100
                except Exception as e:
                        self._logger.error("Fill density setting {} is invalid, must be percentage (integer)".format(str(fill_density_percentage)))
                        fill_density_percentage = None 

                file_name = file_info['name']
                file_path = file_info['path']
                file_target = file_info['target']

                #This is where the slice happens
                if file_name.lower().endswith('.stl') and file_target == 'local':
                        octoprint_api_key = settings().get(['api', 'key']) 
                        layerHeight = float(self._settings.get(['layerHeight']))
                        auto_print_uri = "http://localhost/api/files/local/{}".format(urllib.quote_plus(file_path))
                        
                        #default_slice_profile_name = self._get_default_slice_profile('cura')['key']
                        default_slice_profile_name = self._get_default_slice_profile('cura')
                        print('&' * 30 + str(default_slice_profile_name))
                        printer_profile_name = self._get_current_printer_profile()['id']
                        print('Q' * 30 + str(printer_profile_name))

                        
                        slice_data = {
                                      'command': 'slice',
                                      'profile': default_slice_profile_name,
                                      'printerProfile': printer_profile_name,
                                      'profile.layer_height': layerHeight
                                     }

                        if fill_density_percentage is not None:
                                slice_data['profile.infill'] = fill_density_percentage
                                slice_data['print'] = True
                   

                        assert octoprint_api_key is not None and len(octoprint_api_key) > 0
                        response = requests.post(auto_print_uri, headers = { "X-Api-Key" : octoprint_api_key }, json=slice_data, timeout=HTTP_REQUEST_TIMEOUT)
                        response.raise_for_status()
                        json_response = response.json()
                        
                        return json_response
   
        #on_event
        #a series of if statements containg the different events filtracker listens for.
        #self, event, payload, **kwargs
        #return
	def on_event(self, event, payload, **kwargs):
		global Layer
		global uid
		global url
		did = self._settings.get(["did"])

		self.checkPrinterStatus()
                self._logger.info("event change123:")
                self._logger.info(event)
                self._logger.info(payload)
                event_body = {} 
		if event == "PrintStarted":
			Layer = 0
			self.sendLayerStatus(Layer)
                        self._update_spool_length(update_remote=True)
                        self._update_profile_event_stats(event)
                        self._download_best_profile() 
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
                        self._download_best_profile()
                if event in FiltrackerPrintingStatusDict:
                        self._logger.info("saving printing status event", FiltrackerPrintingStatusDict[event])
                        octoprint.plugin.SettingsPlugin.on_settings_save(self, FiltrackerPrintingStatusDict[event])
                        self._send_printer_status() 
                if event == "Startup" and self._printer.is_printing() is not True:
                         octoprint.plugin.SettingsPlugin.on_settings_save(self, FiltrackerPrintingStatusDict["Idle"])
                if event == "PrinterStateChanged" and "state_string" in payload.keys() and payload["state_string"] == 'Printing':
                        octoprint.plugin.SettingsPlugin.on_settings_save(self, {'PrintingStatus': 'Printing'})
                self._send_printer_status()
        
		if event in FiltrackerMsgDict:    
			event_body = {
				'uid' : uid,
				'did' : did,
				'event' : FiltrackerMsgDict[event]['name'],
				'status' : FiltrackerMsgDict[event]['value']
			}
                        try:
                                requests.post(url, data = event_body)
                        except BadStatusLine:
                                self._logger.info("Filtracker: Bad Status")

		elif event == 'FileSelected':
			event_body = {
				'uid' : uid,
				'did' : did,
				'event' : 'File',
				'status' : payload['filename']
			}
                        try:
                                requests.post(url, data = event_body)
                        except BadStatusLine:
                                self._logger.info("Filtracker: Bad Status")

		elif event == 'ZChange':
			Layer += 1
			event_body = {
				'uid' : uid,
				'did' : did,
				'event' : 'Layer',
				'status' : Layer
			}
                        self._update_spool_length(update_remote=True)
                        try:
                                requests.post(url, data = event_body)
                        except BadStatusLine:
                                self._logger.info("Filtracker: Bad Status")
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
                                self._logger.info("Filtracker: Bad Status")

                        return

	        self._logger.info("Filtracker: Recording event " + event)

        #sendLayerStatus
        #A post to the locbit-edge url with the current layer information
        #self, layer
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
			self._logger.info("Filtracker: Bad Status")

        #CheckPrinterStatus
        #sends a get request to the localhost/api/printer for the current status of the printer
        #self
	def checkPrinterStatus(self):
		url = "http://localhost/api/printer"
		apiKey = settings().get(['api', 'key']) 

		try:
			r = requests.get(url,  headers = { "X-Api-Key" : apiKey })
			self._logger.info(r.text)
		except BadStatusLine:
			self._logger.info("Filtracker: Bad Status")
        
        #is_wizard_required
        #Checks the config.yaml file for the mac address. Does a setup if macaddress not there.
        #self
        #true if no macaddress in the config.yaml file.
        def is_wizard_required(self):
                mac_address = self._settings.get(['macAddress'])

                if not mac_address:
                        return True
                print('5' * 20 + "{}".format(mac_address))

        #_set_events
        #Sets the events and their data to be transmitted trough locbit-edge.
        #self
        #Event_dict(muidname, material, color, diameter, length)
        def _set_events(self):
                from datetime import datetime 
                from pytz import timezone
                import time
               
               #This auto-converts the timezone. 
                hold_zone = str(time.timezone / 3600.0)
                hold = ''
                if float(hold_zone) > 0:
                    hold = "%a, %m-%d-%y %H:%M:%S UTC+" + hold_zone
                else:
                    hold = "%a, %m-%d-%y %H:%M:%S UTC-" + hold_zone

                #Instanciates the variables that will respond to the platform.                
                datetime_str = datetime.now().strftime(hold)
                muidName = str(self._settings.get(["muid"]))
                material = str(self._get_spool_settings()["material"])
                color = str(self._get_spool_settings()["color"])
                diameter = self._get_spool_settings()["diameter"]
                length = str(self._get_spool_settings()["length"])
                from uuid import getnode as get_mac
                did = get_mac()
                printer_status = "Disconnected"
                printer_connection = self._printer.get_current_connection()
                if printer_connection[0] is not "Closed":
                        printer_status = "Connected"
                event_dict = {
                        "did" : did,
                        "PrinterStatus" : printer_status,
                        "PrintingStatus" : self._settings.get(["PrintingStatus"]),
                        "Message" : "",
                        "LastPingTime" : datetime_str
                }

                if len(muidName) > 0:
                        event_dict["MUIDName"] = muidName
                if len(material) > 0:
                        event_dict["Material"] = material
                if len(color) > 0:
                        event_dict["Color"] = color
                if len(diameter) > 0:
                        event_dict["Diameter"] = diameter
                if len(length) > 0 and length >= 0:
                        event_dict['Length'] = length
                return event_dict    

        #_send_printer_status
        #Respnds to locbit-edge with the current state of the printer.
        #self
        def _send_printer_status(self):
                from uuid import getnode as get_mac
                global url
                current_event = self._set_events()
                headers = {'protocol': 'octoprint','protocol-identifier':str(get_mac()),'protocol-payload':settings().get(['api', 'key'])}
                try:
                        response = requests.post(url, data = current_event, headers=headers)
                except BadStatusLine:
                        self._logger.info("Filtracker: Bad Status")

        #_send_printer_with_timer
        #Responds to a call with the set events and a time stamp.
        #self
        def _send_printer_status_with_timer(self):
                import threading        
                global url
                self._send_printer_status()
                int_time = float(self._settings.get(["updateInterval"]))
                try:

                        t = threading.Timer(int_time, self._send_printer_status_with_timer)
                        t.start()
                except BadStatusLine:
                        self._logger.info("Filtracker: Bad Status")

        #action
        #It allows the Locbit cloud to trigger commands on filtracker.
        #self
        #flask response('command sent')
        @octoprint.plugin.BlueprintPlugin.route("/action", methods=["GET"])
        def action(self):
                if request.args.get('command') == 'ping':
                        self._send_printer_status()
                if request.args.get('command') == 'StartPrint':
                        self._printer.start_print()
                if request.args.get('command') == 'ResumePrint':
                        self._printer.resume_print()
                if request.args.get('command') == 'PausePrint':
                        self._printer.pause_print()
                if request.args.get('command') == 'CancelPrint':
                        self._printer.cancel_print()
                if request.args.get('command') == 'CancelPrint':
                        self._printer.cancel_print()
                return flask.make_response("Command Sent.", 200)

__plugin_name__ = "Filtracker"
__plugin_implementation__ = FiltrackerPlugin()
