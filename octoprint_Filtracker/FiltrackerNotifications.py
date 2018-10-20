from __future__ import absolute_import
import octoprint.util
FiltrackerPrinterStatusDict = {
	'PrinterConnected' : {
		'Connected' : 'Connected'
	},
	'PrinterDisconnected' : {
		'Disconnected' : 'Disconnected'
	},
	'PrinterError' : {
		'Error' : 'Error'
	},
	'PrinterUnknown' : {
		'Unknown' : 'Unknown'
	}
}
FiltrackerPrintingStatusDict = {
	'PrintStarted' : {
		'PrintingStatus' : 'Printing'
	},
	'PrintPaused' : {
		'PrintingStatus' : 'Paused'
	},
	'PrintDone' : {
		'PrintingStatus' : 'Complete'
	},
	'PrintCancelled' : {
		'PrintingStatus' : 'Cancelled'
	},
	'PrintFailed' : {
		'PrintingStatus' : 'Failed'
	},
	'PrintResumed' : {
		'PrintingStatus' : 'Resume'
	},
	'PrintingStatus' : {
		'PrintingStatus' : 'Unknown'
	},
	'Idle' : {
		'PrintingStatus' : 'Idle'
	},
	'PRINTING' : {
		'PrintingStatus' : 'Printing'
	},
	'PAUSING' : {
		'PrintingStatus' : 'Pausing'
	},
	'PAUSED' : {
        	'PrintingStatus' : 'Paused'
   	 },
    	'CONNECTING' : {
        	'PrintingStatus' : 'Connecting'
   	 },
    	'OPERATIONAL' : {
        	'PrintingStatus' : 'Idle'
   	 },
    	'ERROR' : {
        	'PrintingStatus' : 'Error'
   	 },
    	'CLOSED_WITH_ERROR' : {
       		'PrintingStatus' : 'CloseWithError'
    	},
    	'TRANSFERING_FILE' : {
        	'PrintingStatus' : 'TransferingFile'
    	},
    	'OFFLINE' : {
        	'PrintingStatus' : 'Offline'
    	},
    	'UNKNOWN' : {
       		'PrintingStatus' : 'Unknown'
   	},
   	'NONE' : {
        	'PrintingStatus' : 'None'
    	},
	'RESUMING' : {
		'PrintingStatus' : 'Resuming'
	}
}
FiltrackerSlicingStatusDict = {
	'SlicingStarted' : {
		'SlicingStarted' : 'Slicing'
	},
	'SlicingDone' : {
		'SlicingDone' : 'Done'
	},
	'SlicingFailed' : {
		'SlicingFailed' : 'Failed'
	},
	'SlicingCancelled' : {
		'SlicingCancelled' : 'Cancelled'
	},
	'SlicingStatus' : {
		'Unknown' : 'Unknown'
	}
}
FiltrackerMsgDict = {
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
