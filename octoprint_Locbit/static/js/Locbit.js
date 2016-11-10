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

        self.onStartup = function() {
            var element = $("#state").find(".accordion-inner .progress");
            if (element.length) {
                var text = gettext("Material Diameter (mm)");
                var text2 = gettext("Color");
                var text3 = gettext("Length (m)");
                var text4 = gettext("MUID");
                element.before(text + ": <br>");
                element.before(text2 + ": <br>");
                element.before(text3 + ": <br>");
                element.before(text4 + ": <br>");
            }
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
