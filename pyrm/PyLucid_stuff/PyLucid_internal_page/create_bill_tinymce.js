if (!tinyMCE) {
    alert("Error: tinyMCE not loaded!");
} else {
    try {
        tinyMCE.init({
            apply_source_formatting : true,
            mode : "textareas",
            height : "300",
            width : "100%",
            plugins : "table",
            theme_advanced_buttons1 : "undo,redo,code,separator,delete_row,row_after",
            theme_advanced_buttons2 : "",
            theme_advanced_buttons3 : "",
            theme : "advanced",
        });
    } catch (e) {
        alert("tinyMCE.init() error:" + e);
    }
}