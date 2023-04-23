#!/usr/bin/python

# graphical user interface for headsetcontrol
import argparse
import logging
import subprocess
import sys

try :
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
    from gi.repository import GLib
except :
    sys.exit("import failed: please ensure that you have the gi (Python API for Introspection) library installed")

from .capabilities import (
    Capabilities,
    Capability)

from .comm import (
    start_checking,
    get_name,
    send_headset)

from .gui import (
    MainWindow,
    ErrorDialog)
    
def main(args=None) :

    # parse command line.
    parser = argparse.ArgumentParser(prog="gheadset",
                                     description="GUI front end to headsetcontrol",
                                     epilog="requires gtk")
    parser.add_argument("-b", "--batterypolltime", required=False, default=60, type=int, help="battery poll time in seconds (default 60; 0 for no poll)")
    parser.add_argument("-c", "--chatmixpolltime", required=False, default=1, type=int, help="chat mix poll time in seconds (default 1; 0 for no poll)")
    parser.add_argument("-d", "--debug", required=False, default=False, action="store_true", help="create GUI with full program capabilities, and log commands.")
    
    args = parser.parse_args()

    if (args.debug) :
        logging.basicConfig(level=logging.DEBUG)
    logging.debug("debug enabled")

    headset_name = get_name()

    # construct headset capabilities table
    # headsetcontrol program options -t and -f are not supported.
    all_capabilities = Capabilities([
        Capability('s', 'sidetone',         'level',          'Sets sidetone, level must be between 0 and 128', max=128),
        Capability('b', 'battery',          '',		   'Checks the battery level', max=100, editable=False),
        Capability('n', 'notificate',       'soundid', 	   'Makes the headset play a notification', max=1),
        Capability('l', 'light',            '0|1', 	   'Switch lights (0 = off, 1 = on)', max=1),
        Capability('i', 'inactive-time',    'time', 	   'Sets inactive time in minutes, time must be between 0 and 90, 0 disables the feature', max=90),
        Capability('m', 'chatmix',          '',   	           'Retrieves the current chat-mix-dial level setting between 0 and 128. Below 64 is the game side and above is the chat side', editable=False, max=128),
        Capability('v', 'voice-prompt',     '0|1', 	   'Turn voice prompts on or off (0 = off, 1 = on)', max=1),
        Capability('r', 'rotate-to-mute ',  '0|1', 	   'Turn rotate to mute feature on or off (0 = off, 1 = on)', max=1),
        Capability('e', 'equalizer',        'string', 	   'Sets equalizer to specified curve, string must contain band values specific to the device (hex or decimal) delimited by spaces, or commas, or new-lines e.g "0x18, 0x18, 0x18, 0x18, 0x18"', default=""),
        Capability('p', 'equalizer-preset', 'number',         'Sets equalizer preset, number must be between 0 and 3, 0 sets the default', max=3),
        #    Capability('f', 'follow',           '[secs timeout]', 'Re-run the commands after the specified seconds timeout or 2 by default', default=2, max=5),
        #    Capability('t', 'timeout',          '(0-100000)',     'Specifies the timeout in ms for reading data from device (default 5000)', default=5000, max=100000)
])

    # ask headset capabilities
    headset_capabilities = Capabilities()
    
    result = send_headset(cmd='?')
    split = result.split('\n')
    for char in split[0] :
        headset_capabilities.insert(all_capabilities.lookup(char))
        
    for cap in headset_capabilities :
        logging.debug("capability:  " + cap.long_option)

    # set up GUI.
    if not args.debug :
        mainWin = MainWindow(headset_name, headset_capabilities)
    else :
        mainWin = MainWindow(headset_name, all_capabilities)

    # start battery check and chat mix timer loops
    if (args.batterypolltime > 0 ) and (headset_capabilities.lookup('b') or args.debug) :
        start_checking(all_capabilities.lookup('b'), args.batterypolltime)

    if (args.chatmixpolltime > 0) and (headset_capabilities.lookup('m') or args.debug) :
        start_checking(all_capabilities.lookup('m'), args.chatmixpolltime)

    # and go!
    mainWin.show_all()
    Gtk.main()

if __name__=="__main__" :
    sys.exit(main())
    
