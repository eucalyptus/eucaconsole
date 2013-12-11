
// JAVASCRIPT SNIPPET TAKEN FROM 3.4.1 TO ADD A LISTENER TO THE FILE UPLOAD INPUTBOX
$('html body').find("#key-import-file").on('change', function(evt) {
    var file = evt.target.files[0];
    var reader = new FileReader();
    reader.onloadend = function(evt) {
        if (evt.target.readyState == FileReader.DONE) {
            $('html body').find("#key-import-contents").val(evt.target.result).trigger('keyup');
        }
    }
    reader.readAsText(file);
});

