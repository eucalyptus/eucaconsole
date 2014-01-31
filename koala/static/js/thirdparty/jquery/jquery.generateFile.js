/*************************************************************************
 * This file may incorporate work covered under the following copyright
 * and permission notice:
 *
 * the original code -- http://tutorialzine.com/2011/05/generating-files-javascript-php/
 * the license term can be found -- http://tutorialzine.com/license/
 ************************************************************************/

(function ($) {
    // Creating a jQuery plugin:
    $.generateFile = function (options) {
        options = options || {};
        if (!options.script || !options.filename || !options.content || !options['csrf_token']) {
            throw new Error("Please enter all the required config options!");
        }
        // Creating a 1 by 1 px invisible iframe:
        var iframe = $('<iframe>', {
            width: 1,
            height: 1,
            frameborder: 0,
            css: {
                display: 'none'
            }
        }).appendTo('body');

        var formHTML = [
            '<form action="" method="post">',
            '<input type="hidden" name="csrf_token" />',
            '<input type="hidden" name="filename" />',
            '<input type="hidden" name="content" />',
            '</form>'
        ].join('');

        // Giving IE a chance to build the DOM in
        // the iframe with a short timeout:
        setTimeout(function () {
            // The body element of the iframe document:
            var body = (iframe.prop('contentDocument') !== undefined) ?
                iframe.prop('contentDocument').body :
                iframe.prop('document').body;  // IE
            body = $(body);

            // Adding the form to the body:
            body.html(formHTML);
            var form = body.find('form');

            form.attr('action', options.script);
            form.find('input[name=csrf_token]').val(options['csrf_token']);
            form.find('input[name=filename]').val(options.filename);
            form.find('input[name=content]').val(options.content);

            // Submitting the form to . This will
            // cause the file download dialog box to appear.

            form.submit();
        }, 50);
    };

})(jQuery);