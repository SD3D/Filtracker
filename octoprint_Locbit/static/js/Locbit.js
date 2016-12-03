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

        function apiFetch() {
            $.ajax({
                type: "GET",
                url: "/api/plugin/Locbit",
                success: function(data) {
                    // $('#material').html(data);
                    if (Object.keys(data).length == 5) {
                        $('#material').html(data.material);
                        $('#diameter').html(data.diameter);
                        $('#color').html(data.color);
                        $('#length').html(data.length);
                        $('#muid').html(data.muid);
                    }
                    else {
                        $('#qr-btn').after('<div id="qr-error">Invalid QR Code</div>');
                        setTimeout(function(){
                            $('#qr-error').remove();
                        }, 2000);

                    }
                }
        });
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

            var code = '<div class="jog-panel"> <!-- QR Code control panel --> <div class="jog-panel" id="scan-qr-code"> <h1>QR Code</h1><div> <button class="btn btn-block control-box" id="qr-btn" data-bind="enable: isOperational() && !isPrinting() && loginState.isUser(), click: function() { } ">Scan QR</button></div></div></div>';

            var controlElement = $("#control");

            controlElement.append(code);

            $( "#qr-btn" ).bind( "click", function() {
                apiFetch();
            });


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
