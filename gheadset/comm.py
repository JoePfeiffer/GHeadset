import logging
import subprocess

try :
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
    from gi.repository import GLib
except :
    sys.exit("import failed: please ensure that you have the gi (Python API for Introspection) library installed")

from .gui import ErrorDialog

def start_checking(cap, poll_time) :
    check_value(cap)

    GLib.timeout_add(poll_time * 1000, check_value, cap)
    
def check_value(cap) :
    logging.debug("checking " + str(cap))
    level = send_headset(cmd=cap.short_option)
    if level is not None :
        cap.setPercent(int(level)/cap.max)
    return True

# Obtain headset name.
def get_name() :
    result  = subprocess.run(['headsetcontrol', '-?'], stdout=subprocess.PIPE)
    split = result.stdout.decode().split('Found ')
    name = split[1].split("!")[0]
    
    logging.debug("headset name " + name)
    return name

# Comm with headset
def send_headset(cmd=None, arg=None) :
        
    # make it easier to parse the result
    optionList = ['-c']
    
    # add command and arg if any
    optionList.append('-' + cmd)
    
    if arg is not None :
        optionList.append(arg)

    # and send it
    cmdline = ['headsetcontrol'] + optionList

    logging.debug("command line: " + str(cmdline))
        
    result = subprocess.run(cmdline, capture_output=True)
    logging.debug("result " + str(result))
    if result.returncode == 0 :
        return result.stdout.decode()
    else :
        # We'll either display the error dialog or log the error, depending
        # on whether debug is turned on
        if logging.root.level != logging.DEBUG :
            ErrorDialog(result.stderr.decode())
        logging.debug(result.stderr.decode())
        return None

    return None
