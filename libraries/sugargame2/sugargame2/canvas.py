import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
import pygame
import event

CANVAS = None

class PygameCanvas(Gtk.EventBox):
    
    """
    activity is the activity intself.
    """
    def __init__(self, activity, pointer_hint=True,
                main=None, modules=[pygame]):
        GObject.GObject.__init__(self)

        global CANVAS
        assert CANVAS == None, "Only one PygameCanvas can be created, ever."
        CANVAS = self

        # Initialize Events translator before widget gets "realized".
        self.translator = event.Translator(activity, self)
        
        self._activity = activity
        self._modules = modules
        self._main = main

        self.set_can_focus(True)
        
        self._socket = Gtk.Socket()
        self._socket.connect('realize', self._realize_cb)
        self.add(self._socket)
        self.show_all()

    def _realize_cb(self, widget):

        # Preinitialize Pygame with the X window ID.
        os.environ['SDL_WINDOWID'] = str(widget.get_id())
        for module in self._modules:
            module.init()

        # Restore the default cursor.
        widget.props.window.set_cursor(None)

        # Confine the Pygame surface to the canvas size
        r = self.get_allocation()
        self._screen = pygame.display.set_mode((r.width, r.height),
                                               pygame.RESIZABLE)

        # Hook certain Pygame functions with GTK equivalents.
        self.translator.hook_pygame()

        # Call the caller's main loop as an idle source
        if self._main:
            GLib.idle_add(self._main)

    def get_pygame_widget(self):
        return self._socket
