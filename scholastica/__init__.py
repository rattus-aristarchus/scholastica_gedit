from gi.repository import GObject, Gedit, Gio, GLib
import os
import threading
import logging
from xmlrpc.client import ServerProxy
from xmlrpc.server import SimpleXMLRPCServer

from scholastica.provider import TagProvider
from scholastica.conf import LOG_FILTER

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ScholasticaPlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "ScholasticaPlugin"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        logger.info("init")
        
        GObject.Object.__init__(self)
                
        #These are necessary to kill signals when cleaning up
        self._providers = {}
        self._doc_signals = {}
        
    def do_activate(self):  
        logger.info("do_activate")
        
        self.proxy = ServerProxy('http://localhost:9000', allow_none=True)
        self.listener = Listener(self.window)
        self.listener.start()
        
        self._tab_added_id = self.window.connect('tab-added', self.on_tab_added)
        self._tab_removed_id = self.window.connect('tab-removed', self.on_tab_removed)
        """
        path = "/media/kryis/TOSHIBA EXT/записи/организатор записей/источник.txt"
        file = Gio.File.new_for_path(path)
        logger.info(f"do_activate: file object created at {file.get_path()}")
        self.window.create_tab_from_location(location=file,
                                             encoding=None,
                                             line_pos=0,
                                             column_pos=0,
                                             create=False,
                                             jump_to=True)
        """
        
    def do_deactivate(self):       
        logger.info("do_deactivate")
        
        self.window.disconnect(self._tab_added_id)
        self.window.disconnect(self._tab_removed_id)
        pass

    def on_tab_added(self, window, tab, data=None):        
        logger.info("on_tab_added")
        
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
        logger.info("on_tab_removed")

        if tab in self._doc_signals:
            doc = tab.get_document()
            doc.disconnect(self._doc_signals[tab][0])
            doc.disconnect(self._doc_signals[tab][1])
        
        if tab in self._providers:
            provider = self._providers[tab]
            tab.get_view().get_completion().remove_provider(provider)

    def on_document_loaded(self, document, data=None):
        logger.info("on_document_loaded")
        
        self.update_file(document)

    def on_document_saved(self, document, data=None):                
        logger.info("on_document_saved")
            
        #Saving a document signals the main application that it can read the file
        self.update_file(document)    

    def do_update_state(self):
        pass
    
    def update_file(self, document):
        logger.info("updating file")
        
        try:
            path = util.document_path(document)
            response = self.proxy.update_file(path)
        except ConnectionRefusedError:
            logger.warning("MAIN: connection to the scholastica application refused, " \
                           + "most likely because it is not currently running")
        return

class Listener(threading.Thread):
    
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.server = SimpleXMLRPCServer(('localhost', 8000), 
                                         logRequests=True,
                                         allow_none=True)
        self.server.register_function(self.open_file, 'open_file')
        
    def run(self):
        try:
            logger.info("Messenger is listening...")
            self.server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Messenger is exiting")
    
    def open_file(self, path, item):
        logger.info(f"Listener: trying to open file {path} at {item}")
        
        def open_file_main_thread():
            logger.info("Listener internal: trying to open file")
            
            try:
                file = Gio.File.new_for_path(path)
                logger.debug(f"Listener internal: file object created at {file.get_path()}")
                tab = self.window.get_tab_from_location(file)
                
                if tab == None:
                    tab = self.window.create_tab_from_location(location=file,
                                                                encoding=None,
                                                                line_pos=0,
                                                                column_pos=0,
                                                                create=False,
                                                                jump_to=True)                
                else:
                    logger.info("Listener internal: tab already exists")
                
                self.window.set_active_tab(tab)
                start = tab.get_document().get_start_iter()
                end = tab.get_document().get_end_iter()
                text = tab.get_document().get_text(start, end, True)
                logger.debug("Listener internal: loaded tab with text: " + text[:100])
                #This is a half-assed solution. What if the text in the tab is not saved yet
                #and there is a change in the segment we're looking for? we can avoid some of
                #those cases by looking for not the whole segment, but just the first 100
                #symbols
                search = item[:100]
                if search in text:
                    before = text[:text.find(search)]
                    line = before.count("\n")
                    logger.debug(f"Listener internal: found search string in text; at line "+
                                 f"{line}")
                    #tab.get_document().goto_line_offset(line, 0)
                    iter = tab.get_document().get_iter_at_line(line)
                    tab.get_document().place_cursor(iter)
                    tab.get_view().scroll_to_cursor()
                else:
                    logger.debug("Listener internal: could not find search string in text")
                    
            except Exception as e:
                logger.error(str(e))

        GLib.idle_add(open_file_main_thread)
