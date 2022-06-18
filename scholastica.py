from gi.repository import GObject, Gedit
import os
from urllib.parse import urlparse
from urllib.parse import unquote
from xmlrpc.client import ServerProxy
import xmlrpc

class ScholasticaPlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "ScholasticaPlugin"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.window.connect('tab-added', self.on_tab_added)
        self.proxy = ServerProxy('http://localhost:9000', allow_none=True)
        return

    def on_tab_added(self, window, tab, data=None):
        doc = tab.get_document()
        doc.connect('saved', self.on_document_saved)
        doc.connect('loaded', self.on_document_loaded)
        return

    def on_document_loaded(self, document, data=None):
        return

    def on_document_saved(self, document, data=None):
        location = document.get_file().get_location()
        uri = location.get_uri()
        path = urlparse(uri).path
        print(path)
        if "%" in path:
            path = unquote(path)
        print(path)
        #byte_s = path.encode('cp1251')
        #utf = byte_s.decode('utf8')
        #print(utf)
        returned_value = self.proxy.on_save(path)
        return
    
    def do_deactivate(self):
        pass

    def do_update_state(self):
        pass
"""
When cleaning up, remember to kill all your signal handlers. Given the above example, cleanup code would look something like this:

l_id = doc.examplePyPluginHandlerId
doc.disconnect(l_id)
doc.examplePyPluginHandlerId = None
"""
