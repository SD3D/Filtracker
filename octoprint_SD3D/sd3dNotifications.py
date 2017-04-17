from __future__ import absolute_import
import octoprint.util

sd3dMsgDict = {
	'Connected' : {
		'name' : 'PrinterStatus',
		'value' : 'Connected'
	},
	'Disconnected' : {
		'name' : 'PrinterStatus',
		'value' : 'Disconnected'
	},
	'Error' : {
		'name' : 'PrinterStatus',
		'value' : 'Error'
	},
	'PrintStarted' : {
		'name' : 'PrintingStatus',
		'value' : 'Printing'
	},
	'PrintFailed' : {
		'name' : 'PrintingStatus',
		'value' : 'Failed'
	},
	'PrintDone' : {
		'name' : 'PrintingStatus',
		'value' : 'Complete'
	},
	'PrintCancelled' : {
		'name' : 'PrintingStatus',
		'value' : 'Cancelled'
	},
	'PrintPaused' : {
		'name' : 'PrintingStatus',
		'value' : 'Paused'
	},
	'PrintResumed' : {
		'name' : 'PrintingStatus',
		'value' : 'Printing'
	},
	'FileDeselected' : {
		'name' : 'File',
		'value' : 'NULL'
	}
}
