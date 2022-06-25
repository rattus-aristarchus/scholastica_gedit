from gi.repository import GtkSource, GObject

class TagProposal(GObject.Object, GtkSource.CompletionProposal):
    
    def __init__(self, name):
        GObject.Object.__init__(self)        
        self.name = name
    
    def do_get_text(self):
        return self.name
    
    def do_get_label(self):
        return self.name
    
    def do_get_info(self):
        return 'No extra info available'

#gobject.type_register(TagProposal) 
