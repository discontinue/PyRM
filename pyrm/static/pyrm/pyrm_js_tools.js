// helper function for console logging
// set debug to true to enable debug logging
function log() {
	//try {debug} catch (e) {debug=false};
    //if (debug && window.console && window.console.log)
    if (window.console && window.console.log)
        window.console.log(Array.prototype.join.call(arguments,''));
}
log("pyrm_js_tools.js loaded.");


function OpenInWindow(link) {
    /*************************************************************************
    Open link in a new JavaScript window.
    Usage e.g.:
        <a href="/foobar/" onclick="return OpenInWindow(this);">foobar</a>
	  *************************************************************************/
    log("OpenInWindow()");
    var url = $(link).attr("href");
    log("url:" + url);
    
    window_name=url;
    window_name = window_name.indexOf('?') > -1 ? window_name.substr(0, window_name.indexOf('?')) : window_name;
    window_name = window_name.indexOf('#') > -1 ? window_name.substr(0, window_name.indexOf('#')) : window_name;
    log("window name:" + window_name);
    
    win = window.open(url, window_name, "width=960, height=760, dependent=yes, resizable=yes, scrollbars=yes");
    win.focus();
    return win;
}



var MIN_ROWS = 1;
var MAX_ROWS = 25;

function set_textarea_size(textarea) {
    rows = textarea.attr("value").split("\n").length;
    
    if (rows > MAX_ROWS) { rows = MAX_ROWS; }
    if (rows < MIN_ROWS) { rows = MIN_ROWS; }

    log("set textarea "+textarea.id+" row to:" + rows);
    
    textarea.css("height", "auto");
    textarea.attr("rows", rows);
}

jQuery(document).ready(function($) {   
    /************************************************************************
	 * Resize all textareas                                                 */
    $("textarea").each(function() {
		set_textarea_size($(this));
		
		$(this).bind("keyup", function(event) {
			var k = event.keyCode 
			//log("key code: " + k);
			/*
			 * 13 == Enter
			 * 8  == backspace
			 * 46 == delete
			 * 17 == Control (for copy&paste: ctrl-c, ctrl-v)
			 */
			if (k==13 || k==8 || k==46 || k==17) {
				set_textarea_size($(this));
			}
		});
    });
});