using Toybox.Application as App;
using Toybox.System as Sys;
using Toybox.Lang as Lang;
using Toybox.WatchUi as Ui;

class BasicApp extends App.AppBase {


    function initialize() {
      App.AppBase.initialize();
    }

    function onSettingsChanged() {
      Ui.requestUpdate();
    }

    //! onStart() is called on application start up
    function onStart(state) {
    }

    //! onStop() is called when your application is exiting
    function onStop(state) {
    }

    //! Return the initial view of your application here
    function getInitialView() {
        	return [ new BasicView() ];
    }

}
