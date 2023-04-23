import logging

try :
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
    from gi.repository import GLib
except :
    sys.exit("import failed: please ensure that you have the gi (Python API for Introspection) library installed")

from .comm import send_headset

# Interaction with headset capabilities
class Capability :
    def __init__(self, short_option, long_option, argument, description, max=0, default=0, editable=True) :
        self.short_option = short_option
        self.long_option = long_option
        self.argument = argument
        self.description = description
        self.default = default
        self.max = max
        self.editable = editable
        self.label = Gtk.Label(label=long_option)
        self.label.set_halign(Gtk.Align.START)

        if editable :
            if type(self.default) == str:
                self.actuator = Gtk.Entry()
                self.actuator.set_hexpand(True)
                self.actuator.connect("activate", self.onEntry)
            elif self.max == 1 :
                self.actuator = Gtk.Switch()
                self.actuator.set_active(default == 1)
                self.actuator.set_hexpand(False)
                self.actuator.connect("notify::active", self.onSwitch)
            elif self.max < 10 :
                self.adjustment = Gtk.Adjustment(value=0, lower=0, upper=max, step_increment=1)
                self.actuator = Gtk.SpinButton(adjustment=self.adjustment, climb_rate=1, digits=0)
                self.actuator.set_value(default)
                self.actuator.set_hexpand(True)
                self.actuator.connect("value-changed", self.onSpin)
            else :
                self.actuator = Gtk.Scale()
                self.actuator.set_range(0, self.max)
                self.actuator.set_digits(0)
                self.actuator.set_draw_value(True)
                self.actuator.set_value(default)
                self.actuator.connect("value-changed", self.onChangeValue)
                self.actuator.set_hexpand(True)

            self.label.set_tooltip_text(description)
            self.actuator.set_tooltip_text(description)

        else:
            # If the level is between 0 and 100 we'll display it;
            # if it's less than 0 we'll display a label saying it's charging
            # hopefully nothing but the battery will ever return a value less than 0w
            self.displayLevel = Gtk.ProgressBar()
            self.displayLevel.set_show_text = True
            self.displayLevel.text = ''
            self.displayLevel.set_fraction(default/100.0)
            self.displayLevel.set_hexpand(True)

            self.displayCharging = Gtk.Label()
            self.displayCharging.set_text("CHARGING")
            self.displayCharging.set_hexpand(True)

            self.actuator = self.displayLevel

    # Read-only capability. If the level is between 0 and 100 we'll display it;
    # if it's less than 0 we'll display a label saying it's charging
    # hopefully nothing but the battery will ever return a value less than 0
    def setPercent(self, value) :
        if value >= 0 :
            if self.actuator != self.displayLevel :
                mainWin.grid.remove(self.actuator)
                self.actuator = self.displayLevel
                mainWin.grid.attach(self.actuator, 1, self.row, 1, 1)
                mainWin.show_all()
            self.actuator.set_fraction(value)
        else :
            if self.actuator != self.displayCharging :
                mainWin.grid.remove(self.actuator)
                self.actuator = self.displayCharging
                mainWin.grid.attach(self.actuator, 1, self.row, 1, 1)
                mainWin.show_all()        

    # String capability (actuator is a Gtk.Entry)
    def onEntry(self, entry) :
        send_headset(self.short_option, entry.get_text())
    
    # Boolean capability (actuator is a Gtk.Switch)
    def onSwitch(self, switch, state) :
        print("switch")
        if switch.get_active() :
            send_headset(self.short_option, 1)
        else :
            send_headset(self.short_option, 0)        
    
    # Selector capability (actuator is a Gtk.SpinButton)
    def onSpin(self, spinButton) :
        send_headset(self.short_option, int(self.actuator.get_value()))
    
    # Fraction capability (actuator is a Gtk.Scale)
    def onChangeValue(self, scroll) :
        logging.debug(self.long_option)
        logging.debug(scroll)
        send_headset(self.short_option, str(int(self.actuator.get_value())))

    def __str__(self) :
        return self.long_option

class Capabilities :
    def __init__(self, capabilitiesList = []) :
        self.cap_dict = {}
        self.key_list = []
        for capability in capabilitiesList :
            self.insert(capability)
        
    def insert(self, capability) :
        self.key_list.append(capability.short_option)
        self.cap_dict[capability.short_option] = capability

    def lookup(self, key) :
        return self.cap_dict.get(key)

    def __len__(self) :
        return len(self.cap_dict)

    def __iter__(self) :
        return CapabilitiesIterator(self)
    
class CapabilitiesIterator :
    def __init__(self, capabilities) :
        self.keys = capabilities.key_list
        self.capabilities = capabilities
        self.current_index = 0

    def __iter__(self) :
        return self

    def __next__(self) :
        if self.current_index < len(self.capabilities) :
            self.cap = self.capabilities.lookup(self.keys[self.current_index])
            self.current_index = self.current_index + 1
            return self.cap
        raise StopIteration
