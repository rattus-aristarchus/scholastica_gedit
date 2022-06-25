from gi.repository import GObject, Gedit
import os
from xmlrpc.client import ServerProxy

from scholastica.provider import TagProvider
from scholastica.conf import LOG_FILTER

class ScholasticaPlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "ScholasticaPlugin"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):        
        if (LOG_FILTER < 1):
            print("MAIN: init")
            
        GObject.Object.__init__(self)
        self.proxy = ServerProxy('http://localhost:9000', allow_none=True) 
        #self.provider = TagProvider(self.proxy)
        
    def do_activate(self):          
        if (LOG_FILTER < 1):
            print("MAIN: do_activate")
            
        self.window.connect('tab-added', self.on_tab_added)
        return
    
    def do_deactivate(self):
        pass

    def on_tab_added(self, window, tab, data=None):        
        if (LOG_FILTER < 1):
            print("MAIN: on_tab_added")
        
        doc = tab.get_document()
        doc.connect('saved', self.on_document_saved)
        doc.connect('loaded', self.on_document_loaded)
        
        provider = TagProvider(self.proxy, doc)
        tab.get_view().get_completion().add_provider(provider)
        return

    def on_tab_removed(self, window, tab, data=None):        
        if (LOG_FILTER < 1):
            print("MAIN: on_tab_removed")
            
  #      tab.get_view().get_completion().remove_provider(self.provider)

    def on_document_loaded(self, document, data=None):
        return

    def on_document_saved(self, document, data=None):                
        if (LOG_FILTER < 1):
            print("MAIN: on_document_saved")
            
        try:
            path = util.document_path(document)
            returned_value = self.proxy.on_save(path)
        except ConnectionRefusedError:
            if (LOG_FILTER < 2):
                print("MAIN: connection to the scholastica application refused, " \
                      + "most likely because it is not currently running")
#        tags = self.proxy.query_tags()
 #       for tag in tags:
  #          print(tag)
        return
    

    def do_update_state(self):
        pass
"""
When cleaning up, remember to kill all your signal handlers. Given the above example, cleanup code would look something like this:

l_id = doc.examplePyPluginHandlerId
doc.disconnect(l_id)
doc.examplePyPluginHandlerId = None
"""
 
