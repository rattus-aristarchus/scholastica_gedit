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
        
        #These are necessary to kill signals when cleaning up
        self._providers = {}
        self._doc_signals = {}
        
    def do_activate(self):          
        if (LOG_FILTER < 1):
            print("MAIN: do_activate")
            
        self._tab_added_id = self.window.connect('tab-added', self.on_tab_added)
        self._tab_removed_id = self.window.connect('tab-removed', self.on_tab_removed)
        return
    
    def do_deactivate(self):       
        if (LOG_FILTER < 1):
            print("MAIN: do_deactivate")
        
        self.window.disconnect(self._tab_added_id)
        self.window.disconnect(self._tab_removed_id)
        pass

    def on_tab_added(self, window, tab, data=None):        
        if (LOG_FILTER < 1):
            print("MAIN: on_tab_added")
        
        doc = tab.get_document()
        doc_saved = doc.connect('saved', self.on_document_saved)
        doc_loaded = doc.connect('loaded', self.on_document_loaded)
        self._doc_signals[tab] = [doc_saved, doc_loaded]

        #The object that manages autocompletion
        provider = TagProvider(self.proxy, doc)
        tab.get_view().get_completion().add_provider(provider)
        self._providers[tab] = provider
        return

    def on_tab_removed(self, window, tab, data=None):        
        if (LOG_FILTER < 1):
            print("MAIN: on_tab_removed")

        if tab in self._doc_signals:
            doc = tab.get_document()
            doc.disconnect(self._doc_signals[tab][0])
            doc.disconnect(self._doc_signals[tab][1])
        
        if tab in self._providers:
            provider = self._providers[tab]
            tab.get_view().get_completion().remove_provider(provider)

    def on_document_loaded(self, document, data=None):
        return

    def on_document_saved(self, document, data=None):                
        if (LOG_FILTER < 1):
            print("MAIN: on_document_saved")
            
        #Saving a document signals the main application that it can read the file
        try:
            path = util.document_path(document)
            returned_value = self.proxy.on_save(path)
        except ConnectionRefusedError:
            if (LOG_FILTER < 2):
                print("MAIN: connection to the scholastica application refused, " \
                      + "most likely because it is not currently running")
        return
    

    def do_update_state(self):
        pass
