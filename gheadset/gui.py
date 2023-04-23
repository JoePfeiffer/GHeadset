try :
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
    from gi.repository import GLib
except :
    sys.exit("import failed: please ensure that you have the gi (Python API for Introspection) library installed")

# GUI -- mainwindow
class MainWindow(Gtk.ApplicationWindow):
    def quit(self, button) :
        Gtk.main_quit()
        
    def __init__(self, title, capabilities, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_title(title)
        
        self.outerbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.outerbox.set_spacing(20)
        self.add(self.outerbox)

        self.innerframe = Gtk.Frame()
        self.innerframe.set_shadow_type(Gtk.ShadowType.NONE)
        self.outerbox.add(self.innerframe)
        
        self.grid = Gtk.Grid()
        self.innerframe.add(self.grid)

        # we'll sort the capabilities so user-modifiable parameters come first
        row = 0
        for cap in capabilities :
            if cap.editable :
                self.grid.attach(cap.label, 0, row, 1, 1)
                self.grid.attach(cap.actuator, 1, row, 1, 1)
                cap.row = row
                row = row + 1
                
        for cap in capabilities :
            if not cap.editable :
                self.grid.attach(cap.label, 0, row, 1, 1)
                self.grid.attach(cap.actuator, 1, row, 1, 1)
                cap.row = row
                row = row + 1
        
        self.innerbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.innerbox.set_halign(Gtk.Align.END)
        self.outerbox.pack_start(self.innerbox, False, False, 0)
        
        self.button = Gtk.Button(label="Quit")
        self.button.connect('clicked', self.quit)
        self.innerbox.pack_start(self.button, False, False, 0)

class ErrorDialog(Gtk.MessageDialog) :
    def __init__(self, message) :
        super().__init__(title="Unable to Communicate With Headset",
                         text="Unable to Communicate With Headset",
                         parent = None,
                         buttons = Gtk.ButtonsType.OK)
        self.format_secondary_text(message)
        self.run()
        self.destroy()
