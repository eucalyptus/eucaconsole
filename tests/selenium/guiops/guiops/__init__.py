__author__ = 'alicehubenko'





import os
import re
import sys
import traceback
import StringIO
import struct
import types
import fcntl
import termios
from functools import wraps

# Force ansi escape sequences (markup) in output.
# This can also be set as an env var
_EUTESTER_FORCE_ANSI_ESCAPE = False
# Allow ansi color codes outside the standard range. For example some systems support
# a high intensity color range from 90-109.
# This can also be set as an env var
_EUTESTER_NON_STANDARD_ANSI_SUPPORT = False


class TextStyle():
    BOLD = 1
    FAINT = 2
    ITALIC = 3
    UNDERLINE = 4
    BLINK = 5
    BLINK_FAST = 6
    INVERSE = 7
    CONCEAL = 8
    STRIKED = 9
    html_tag_map = {
        BOLD: 'b',
        FAINT: None,
        ITALIC: 'i',
        UNDERLINE: 'u',
        BLINK: 'blink',
        BLINK_FAST: 'blink',
        INVERSE: None,
        CONCEAL: None,
        STRIKED: 'del',
    }


class ForegroundColor():
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37


class BackGroundColor():
    BG_BLACK = 40
    BG_RED = 41
    BG_GREEN = 42
    BG_YELLOW = 43
    BG_BLUE = 44
    BG_MAGENTA = 45
    BG_CYAN = 46
    BG_WHITE = 47


def markup(text, markups=[1], resetvalue="\033[0m", force=None, allow_nonstandard=None,
           do_html=False, html_open="<", html_close=">"):
    """
    Convenience method for using ansi markup. Attempts to check if terminal supports
    ansi escape sequences for text markups. If so will return a marked up version of the
    text supplied using the markups provided.
    Some example markeups: 1 = bold, 4 = underline, 94 = blue or markups=[1, 4, 94]
    :param text: string/buffer to be marked up
    :param markups: a value or list of values representing ansi codes.
    :param resetvalue: string used to reset the terminal, default: "\33[0m"
    :param force: boolean, if set will add escape sequences regardless of tty. Defaults to the
                  class attr '_EUTESTER_FORCE_ANSI_ESCAPE' or the env variable:
                  'EUTESTER_FORCE_ANSI_ESCAPE' if it is set.
    :param allow_nonstandard: boolean, if True all markup values will be used. If false
                              the method will attempt to remap the markup value to a
                              standard ansi value to support tools such as Jenkins, etc.
                              Defaults to the class attr '._EUTESTER_NON_STANDARD_ANSI_SUPPORT'
                              or the environment variable 'EUTESTER_NON_STANDARD_ANSI_SUPPORT'
                              if set.
    :param do_html: boolean, if True will attempt to convert the ascii escape sequences into
                    similar html tags/output
    returns a string with the provided 'text' formatted within ansi escape sequences
    """
    text = str(text)
    if not markups:
        return text
    if not isinstance(markups, list):
        markups = [markups]
    if do_html:
        startmarkup, endmarkup = _ascii_markups_to_html_tags(markups, open_bracket=html_open,
                                                             close_bracket=html_close)
    else:
        if force is None:
            force = os.environ.get('EUTESTER_FORCE_ANSI_ESCAPE', _EUTESTER_FORCE_ANSI_ESCAPE)
            if str(force).upper() == 'TRUE':
                force = True
            else:
                force = False
        if allow_nonstandard is None:
            allow_nonstandard = os.environ.get('EUTESTER_NON_STANDARD_ANSI_SUPPORT',
                                               _EUTESTER_NON_STANDARD_ANSI_SUPPORT)
            if str(allow_nonstandard).upper() == 'TRUE':
                allow_nonstandard = True
            else:
                allow_nonstandard = False
        if not force:
            if not (hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()):
                return text
        if not allow_nonstandard:
            markups = _standardize_markups(markups)

        markupvalues = ";".join(str(x) for x in markups)
        startmarkup = '\033[{0}m'.format(markupvalues)
        endmarkup = '\033[0m'
    lines = []
    for line in text.splitlines():
        lines.append("{0}{1}{2}".format(startmarkup, line, endmarkup))
    buf = "\n".join(lines)
    if text.endswith('\n') and not buf.endswith('\n'):
        buf += '\n'
    return buf


def _standardize_markups(markups):
    newmarkups = []
    if markups:
        if not isinstance(markups, list):
            markups = []
        for markup in markups:
            if markup > 90:
                newmarkups.append(markup-60)
            else:
                newmarkups.append(markup)
    return newmarkups


def _ascii_markups_to_html_tags(markups, open_bracket="<", close_bracket=">"):
    # '<font color="red">This is some text!</font>'
    color = None
    style_tags = []
    start_tag = ""
    end_tag = ""
    markups = _standardize_markups(markups)
    for value in markups:
        if not color:
            for fg_color in dir(ForegroundColor):
                if getattr(ForegroundColor, fg_color) == value:
                    color = fg_color
            if value in TextStyle.html_tag_map and TextStyle.html_tag_map[value]:
                style_tags.append(TextStyle.html_tag_map[value])
    for tag in style_tags:
        start_tag = "{0}{1}{2}{3}".format(start_tag, open_bracket, tag, close_bracket)
        end_tag = "{0}/{1}{2}{3}".format(open_bracket, tag, close_bracket, end_tag)
    if color:
        start_tag = "{0}{1}".format('{0}font color="{1}"{2}'
                                    .format(open_bracket, color, close_bracket), start_tag)
        end_tag = "{0}{1}".format(end_tag, "{0}/font{1}".format(open_bracket, close_bracket))
    return (start_tag, end_tag)


def get_traceback():
        '''
        Returns a string buffer with traceback, to be used for debug/info purposes.
        '''
        try:
            out = StringIO.StringIO()
            traceback.print_exception(*sys.exc_info(), file=out)
            out.seek(0)
            buf = out.read()
        except Exception, e:
                buf = "Could not get traceback"+str(e)
        return str(buf)


def get_terminal_size():
    '''
    Attempts to get terminal size. Currently only Linux.
    returns (height, width)
    '''
    h = 30
    w = 80
    try:
        # todo Add Windows support
        t_h, t_w = struct.unpack('hh', fcntl.ioctl(sys.stdout,
                                                   termios.TIOCGWINSZ,
                                                   '1234'))
        # Temp hack. Some env will return <= 1
        if t_h > 1 and t_w > 1:
            h = t_h
            w = t_w
    except:
        pass
    return (h, w)


def printinfo(func):
    '''
    Decorator to print method positional and keyword args when decorated method is called
    usage:
    @printinfo
    def myfunction(self, arg1, arg2, kwarg1=defaultval):
        stuff = dostuff(arg1, arg2, kwarg1)
        return stuff
    When the method is run it will produce debug output showing info as to how the
    method was called, example:

    myfunction(arg1=123, arg2='abc', kwarg='words)

    2013-02-07 14:46:58,928] [DEBUG]:(mydir/myfile.py:1234) - Starting method: myfunction()
    2013-02-07 14:46:58,928] [DEBUG]:---> myfunction(self, arg1=123, arg2=abc, kwarg='words')
    '''

    @wraps(func)
    def methdecor(*func_args, **func_kwargs):
        _args_dict = {}  # If method has this kwarg populate with args here
        try:
            defaults = func.func_defaults
            kw_count = len(defaults or [])
            selfobj = None
            arg_count = func.func_code.co_argcount - kw_count
            var_names = func.func_code.co_varnames[:func.func_code.co_argcount]
            arg_names = var_names[:arg_count]
            kw_names = var_names[arg_count:func.func_code.co_argcount]
            kw_defaults = {}
            for kw_name in kw_names:
                kw_defaults[kw_name] = defaults[kw_names.index(kw_name)]
            arg_string = ''
            # If the underlying method is using a special kwarg named
            # '_args_dict' then provide all the args & kwargs it was
            # called with in that dict for inspection with that method
            if 'self' in var_names and len(func_args) <= 1:
                func_args_empty = True
            else:
                func_args_empty = False
            if (not func_args_empty or func_kwargs) and '_args_dict' in kw_names:
                if '_args_dict' not in func_kwargs or not func_kwargs['_args_dict']:
                    func_kwargs['_args_dict'] = {'args': func_args,
                                                 'kwargs': func_kwargs}
            # iterate on func_args instead of arg_names to make sure we pull out
            # self object if present
            for count, arg in enumerate(func_args):
                if count == 0 and var_names[0] == 'self':  # and if hasattr(arg, func.func_name):
                    # self was passed don't print obj addr, and save obj for later
                    arg_string += 'self'
                    selfobj = arg
                elif count >= arg_count:
                    # Handle case where kw args are passed w/o key word as a positional arg add
                    # Add it to the kw_defaults so it gets printed later
                    kw_defaults[var_names[count]] = arg
                else:
                    # This is a positional arg so grab name from arg_names list
                    arg_string += ', '
                    arg_string += str(arg_names[count])+'='+str(arg)
            kw_string = ""
            for kw in kw_names:
                kw_string += ', '+str(kw)+'='
                if kw in func_kwargs:
                    kw_string += str(func_kwargs[kw])
                else:
                    kw_string += str(kw_defaults[kw])
            debugstring = '\n--->(' + str(os.path.basename(func.func_code.co_filename)) + \
                          ":" + str(func.func_code.co_firstlineno) + ")Starting method: " + \
                          str(func.func_name) + '(' + arg_string + kw_string + ')'
            debugmethod = None
            if selfobj and hasattr(selfobj, 'log'):
                logger = getattr(selfobj, 'log', None)
                debug = getattr(logger, 'debug', None)
                if isinstance(debug, types.MethodType):
                    debugmethod = debug
            if debugmethod:
                debugmethod(debugstring)
            else:
                print debugstring
        except Exception, e:
            print get_traceback()
            print 'printinfo method decorator error:' + str(e)
        return func(*func_args, **func_kwargs)
    return methdecor

def get_line(length=None):
    line = ""
    if not length:
        try:
            length = get_terminal_size()[1]
            if length <= 1:
                length = 80
        except:
            length = 80
    for x in xrange(0,int(length-2)):
        line += "-"
        return "\n" + line + "\n"