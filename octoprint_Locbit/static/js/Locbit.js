/*
 * View model for OctoPrint-Locbit
 *
 * Author: Brandon Herbert
 * License: AGPLv3
 */
$(function() {
    function LocbitViewModel(parameters) {
        var printerState = parameters[0];
        var settingsState = parameters[1];
        var filesState = parameters[2];
        var self = this;


        function setQRData(qr_data){
            $('#material').html(qr_data.material);
            $('#diameter').html(qr_data.diameter);
            $('#color').html(qr_data.color);
            $('#length').html(qr_data.length);
            $('#muid').html(qr_data.muid);
        }

        function apiFetch() {

            $('#qr-btn').prop('disabled', true);

            $.ajax({
                type: "GET",
                url: "/api/plugin/Locbit",
                success: function(data) {
                    // $('#material').html(data);
                  if (data.hasOwnProperty('result')){
                    //alert(Object.keys(data.result).length)
                    if (Object.keys(data.result).length == 5) {
                                                
                        setQRData(data.result);

                        if (data.hasOwnProperty('locbit_error')){
                            alert("WARNING - remote locbit connection error: " + data.locbit_error);
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

           $.ajax({
                type: "GET",
                url: "/api/plugin/Locbit?settings=1",
                success: function(data) {
                    // $('#material').html(data);
                  if (data.hasOwnProperty('result')){
                    //alert(Object.keys(data.result).length)
                    if (Object.keys(data.result).length == 5) {

                        setQRData(data.result);

                    }
                    else {

                        alert('Settings error, invalid format.')
                    }
                    
                }
                else if (data.hasOwnProperty('error')){
                     
                     alert("Error: " + data.error);
                }
        }});
        }

        function QRSettingsWrap(payload){
            return getQRSettings();
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
            }

         self.onEventZChange = getQRSettings;
         self.onEventPrintStarted = QRSettingsWrap;
         self.onEventPrintFailed = QRSettingsWrap;
         self.onEventPrintDone = QRSettingsWrap;
         self.onEventPrintCancelled = QRSettingsWrap;
         self.onEventPrintPaused = self.updateSettings;
         self.onPrintResumed = self.updateSettings;

            var code = '<div class="jog-panel"> <!-- QR Code control panel --> <div class="jog-panel" id="scan-qr-code"> <h1>QR Code</h1><div> <button class="btn btn-block control-box" id="qr-btn" data-bind="enable: isOperational() && !isPrinting() && loginState.isUser(), click: function() { } ">Scan QR</button></div></div></div>';

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
        LocbitViewModel,
        ["printerStateViewModel", "settingsViewModel", "gcodeFilesViewModel"],
        []
    ]);
});
