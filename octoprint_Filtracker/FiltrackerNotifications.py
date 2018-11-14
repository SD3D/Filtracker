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
	'Disconnecting' : {
		'PrintingStatus' : 'Disconnecting'
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
      	 	'PrintingStatus' : 'Error'
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
	 },
	'CANCELLING' : {
		'PrintingStatus' : 'Cancelling'
	}
}
FiltrackerPrinterProcessDict = {
	'PrintStarted' : {
		'PrinterProcess' : 'Printing'
	},
	'PrintPaused' : {
		'PrinterProcess' : 'Paused'
	},
	'PrintDone' : {
		'PrinterProcess' : 'Complete'
	},
	'PrintCancelled' : {
		'PrinterProcess' : 'Cancelled'
	},
	'PrintFailed' : {
		'PrinterProcess' : 'Failed'
	},
	'PrintResumed' : {
		'PrinterProcess' : 'Resume'
	},
	'PrintingStatus' : {
		'PrinterProcess' : 'Unknown'
	},
	'Idle' : {
		'PrinterProcess' : 'Idle'
	},
	'Disconnecting' : {
		'PrinterProcess' : 'Disconnecting'
	},
	'PRINTING' : {
		'PrinterProcess' : 'Printing'
	},
	'PAUSING' : {
		'PrinterProcess' : 'Pausing'
	},
	'PAUSED' : {
        	'PrinterProcess' : 'Paused'
   	 },
    	'CONNECTING' : {
        	'PrinterProcess' : 'Connecting'
   	 },
    	'OPERATIONAL' : {
       		'PrinterProcess' : 'Operational'
   	 },
    	'ERROR' : {
        	'PrinterProcess' : 'Error'
   	 },
    	'CLOSED_WITH_ERROR' : {
       		'PrinterProcess' : 'FailedWithError'
    	 },
    	'TRANSFERING_FILE' : {
        	'PrinterProcess' : 'TransferingFile'
    	 },
    	'OFFLINE' : {
        	'PrinterProcess' : 'Offline'
    	 },
    	'UNKNOWN' : {
       		'PrinterProcess' : 'Unknown'
   	 },
   	'NONE' : {
        'PrinterProcess' : 'None'
    },
	'RESUMING' : {
		'PrinterProcess' : 'ResumingPrint'
	},
	'ConnectivityChanged' : {
		'PrinterProcess' : 'ConnectionChanged'
	},
	'FirmwareData' : {
		'PrinterProcess' : 'FirmwareLoaded'
	},
	'FileAdded' : {
		'PrinterProcess' : 'FileAdded'
	},
	'UpdatedFiles' : {
		'PrinterProcess' : 'UpdatedFileList'
	},
	'MetadataAnalysisStarted' : {
		'PrinterProcess' : 'StartingFileAnalysis'
	},
	'Upload' : {
		'PrinterProcess' : 'FileUploadInitiated'
	},
	'MetadataAnalysisFinished' : {
		'PrinterProcess' : 'FileAnalysisComplete'
	},
	'PrintStarted' : {
		'PrinterProcess' : 'PrintStarted'
	},
	'Home' : {
		'PrinterProcess' : 'HomeAxis'
	},
	'ToolChange' : {
		'PrinterProcess' : 'ToolChange'
	},
	'ZChange' : {
		'PrinterProcess' : 'LayerChange'
	},
	'MetadataStatisticsUpdated' : {
		'PrinterProcess' : 'UpdatedProcessStats'
	},
	'PrintCancelling' : {
		'PrinterProcess' : 'CancellingPrint'
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
		'name' : 'PrintingStatus',
		'value' : 'Error'
	},
	'Idle' : {
		'name' : 'PrintingStatus',
		'value' : 'Idle'
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
	'ConnectivityChanged' : {
		'name' : 'PrinterProcess',
		'value' : 'ConnectionChanged'
	},
	'FirmwareData' : {
		'name' : 'PrinterProcess',
		'value' : 'FirmwareLoaded'
	},
	'FileAdded' : {
		'name' : 'PrinterProcess',
		'value' : 'FileAdded'
	},
	'UpdatedFiles' : {
		'name' : 'PrinterProcess',
		'value' : 'UpdatedFileList'
	},
	'MetadataAnalysisStarted' : {
		'name' : 'PrinterProcess',
		'value' : 'StartingFileAnalysis'
	},
	'Upload' : {
		'name' : 'PrinterProcess',
		'value' : 'FileUploadInitiated'
	},
	'MetadataAnalysisFinished' : {
		'name' : 'PrinterProcess',
		'value' : 'FileAnalysisComplete'
	},
	'MetadataStatisticsUpdated' : {
		'name' : 'PrinterProcess',
		'value' : 'UpdatedProcessStats'
	},
	'Home' : {
		'name' : 'PrinterProcess',
		'value' : 'HomeAxis'
	},
	'ToolChange' : {
		'name' : 'PrinterProcess',
		'value' : 'ToolChange'
	},
	'ZChange' : {
		'name' : 'PrinterProcess',
		'value' : 'LayerChange'
	},
	'Connecting' : {
		'name' : 'PrinterProcess',
		'value' : 'Connecting'
	},
	'Disconnecting' : {
		'name' : 'PrinterProcess',
		'value' : 'Disconnecting'
	},
	'FileDeselected' : {
		'name' : 'File',
		'value' : 'NULL'
	}
}
