/*
 * View model for OctoPrint-Filtracker
 */
$(function() {
    function FiltrackerViewModel(parameters) {
        var printerState = parameters[0];
        var settingsState = parameters[1];
        var filesState = parameters[2];
        var filesViewModel = parameters[3];
        var self = this;

        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "Filtracker") {
				// console.log('Ignoring '+plugin);
                return;
            }

            new PNotify({
                         title: 'Alert',
                         text: data 
                        });
			
	}


        function setQRData(qr_data){
            $('#material').html(qr_data.material);
            $('#diameter').html(qr_data.diameter);
            $('#color').html(qr_data.color);
            $('#length').html(qr_data.length);
            $('#muid').html(qr_data.muid);
        }

        self.installDeps = function() {
            
            $('#install-btn').prop('disabled', true);
            var install_url = "/api/plugin/Filtracker?install=1&fill=" + $("#fillPercentInstall").val(); 

            $.ajax({
                    type: "GET",
                    async: true,
                    url: install_url,
                    success: function(data) {
                                             if (data.hasOwnProperty('result')){
                                                   alert("Install completed successfully. Click finish to proceed.");
                                                }

                                                else if (data.hasOwnProperty('error')){
                                                         $('#install-btn').prop('disabled', false);
                                                         alert("Error: " + data.error);
                                                }
                                        }});
        }
 
        function apiFetch() {

            $('#qr-btn').prop('disabled', true);

            $.ajax({
                type: "GET",
                url: "/api/plugin/Filtracker",
                success: function(data) {
                    // $('#material').html(data);
                  if (data.hasOwnProperty('result')){
                    //alert(Object.keys(data.result).length)
                    if (Object.keys(data.result).length == 5) {
                                                
                        setQRData(data.result);

                        if (data.hasOwnProperty('Filtracker_error')){
                            alert("WARNING - " + data.Filtracker_error);
                        }
                        else{
                            new PNotify({
                                         title: 'QR code scan successful',
				         type: 'success',
                                         text: 'Material attributes have been updated'
                                       });
                        }
                    }
                    else {
                        
                        alert('Invalid QR code. Please scan again.')
                    }
 
                    $('#qr-btn').prop('disabled', false);

                }
                else if (data.hasOwnProperty('error')){
                     $('#qr-btn').prop('disabled', false);
                     alert("Error: " + data.error);
                }
        }});
        }

        function getQRSettings(){

           return $.ajax({
                          type: "GET",
                          async: false,
                          url: "/api/plugin/Filtracker?settings=1",
                          success: function(data) {
                          // $('#material').html(data);
                          if (data.hasOwnProperty('result')){
                          //alert(Object.keys(data.result).length)
                          if (Object.keys(data.result).length == 5) {
                          //console.log(data.result);
                          setQRData(data.result);
                       
                          return data;

                         }
                         else {

                              alert('Settings error, invalid format.')
                        }
                    
                       }
                       else if (data.hasOwnProperty('error')){
                     
                              alert("Error: " + data.error);
                      }

                      return undefined;
        }});
        }

        function QRSettingsWrap(payload){
            return getQRSettings();
        }

        function evaluatePrintLength(file){
            estimated_length = file["gcodeAnalysis"]["filament"]["tool0"]["length"];
            
            if(!estimated_length){
                alert("Warning: Remaining filament length unknown. Scan a valid material QR code before proceeding to enable material tracking, or click 'Print' to override.");
                return false;
            }

            qr_data_obj = getQRSettings().responseJSON.result;

            if((qr_data_obj === undefined) || (qr_data_obj === null)){
                alert("Warning: Remaining filament length unknown. Scan a valid material QR code before proceeding to enable material tracking, or click 'Print' to override.");
                return false;
                
            }

            remaining_length_float = parseFloat(qr_data_obj.length);
            estimated_length_float = parseFloat(estimated_length);

            if(remaining_length_float < (estimated_length_float / 1000)){
                alert("Warning: Remaining filament length is insufficient to complete this print. Click 'Print' to override.")
                return false;
            }

            return true;
        }


        function FiltrackerLoadFile(file, printAfterLoad){
            
            if (!file) {
                return;
            }
            var withinPrintDimensions = filesState.evaluatePrintDimensions(file, true);
            var adequateLength = evaluatePrintLength(file);
            var print = printAfterLoad && withinPrintDimensions && adequateLength;

            OctoPrint.files.select(file.origin, file.path, print);

        }

        function FiltrackerFilesUploadDoneWrap(handleUploadFunc){
            
            FiltrackerFilesUploadDone = function(e, data){
                                        handleUploadFunc(e, data);

                                        $.ajax({
                                                type: "GET",
                                                async: false,
                                                url: "/api/plugin/Filtracker?autoprint_setting=1",
                                                success: function(data) {
                                                if (data.hasOwnProperty('result')){
                                                    if(data.result === true){
                                                        $("#slicing_configuration_dialog").modal("hide");
                                                    }
                                                   
                                                }

                                                else if (data.hasOwnProperty('error')){

                                                         alert("Error: " + data.error);
                                                }
                                        }});
                                       }

            return FiltrackerFilesUploadDone;
        }
        

        self.onStartup = function() {
            var element = $("#state").find(".accordion-inner .progress");
            if (element.length) {
                var text0 = gettext("Material");
                var text = gettext("Material Diameter (mm)");
                var text2 = gettext("Color");
                var text3 = gettext("Length (m)");
                var text4 = gettext("MUID");
                element.before(text0 + ": <strong id='material'></strong><br>");
                element.before(text + ": <strong id='diameter'></strong><br>");
                element.before(text2 + ": <strong id='color'></strong><br>");
                element.before(text3 + ": <strong id='length'></strong><br>");
                element.before(text4 + ": <strong id='muid'></strong><br>");

                filesState.loadFile = FiltrackerLoadFile;
                filesViewModel._handleUploadDone = FiltrackerFilesUploadDoneWrap(filesViewModel._handleUploadDone)
                
            }

         self.onEventZChange = getQRSettings;
         self.onEventPrintStarted = QRSettingsWrap;
         self.onEventPrintFailed = QRSettingsWrap;
         self.onEventPrintDone = QRSettingsWrap;
         self.onEventPrintCancelled = QRSettingsWrap;
         self.onEventPrintPaused = self.updateSettings;
         self.onPrintResumed = self.updateSettings;

            var code = '<div class="jog-panel"> <!-- QR Code control panel --> <div class="jog-panel" id="scan-qr-code"> <h1>Material</h1><div> <button class="btn btn-block control-box" id="qr-btn" data-bind="enable: isOperational() && !isPrinting() && loginState.isUser(), click: function() { } ">Scan QR</button></div></div></div>';

            var controlElement = $("#control");

            controlElement.append(code);

            $( "#qr-btn" ).bind( "click", function() {
                apiFetch();
            });
     
            getQRSettings();

        };



        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        // TODO: Implement your plugin's view model here.
    }

    // view model class, parameters for constructor, container to bind to
    OCTOPRINT_VIEWMODELS.push([
        FiltrackerViewModel,
        ["printerStateViewModel", "settingsViewModel", "gcodeFilesViewModel", "filesViewModel"],
        ["#wizard_plugin_Filtracker"]
    ]);
});
