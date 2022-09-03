from gi.repository import GtkSource, GObject
import logging
import scholastica.conf as conf

from scholastica.proposal import TagProposal
import scholastica.util as util

logging.basicConfig(filename=conf.LOGS_FILE,
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TagProvider(GObject.Object, GtkSource.CompletionProvider):

    def __init__(self, proxy, document):
        GObject.Object.__init__(self)
        self.proxy = proxy
        self.document = document

    # TODO: check the performance of this thing with a large file of tags
    # TODO: it might be useful to have the autocompletion look for previous instances of
    # source truncating (e. g. surname of first author, first name of title etc., but
    # i'll have to figure out a way to do it without traversing the whole document every
    # time
    def do_populate(self, context):        
        logger.info("TAG_PROVIDER: do_populate")

        line = util.get_line(context.get_iter()[1])
        phrase = util.get_phrase(context.get_iter()[1])
        if util.enclosed_line(line) and len(phrase) > 1:
            logger.debug("TAG_PROVIDER: got an enclosed line, " + line)
            try:
                sources = self.proxy.query_sources(util.document_path(self.document))
                trunc_sources = [util.truncate_source(source) for source in sources]
                tags = self.proxy.query_tags()
                filtered = self.get_filtered_proposals(trunc_sources + tags, phrase)
                proposals = []
                for name in filtered: 
                    proposals.append(TagProposal(name))
                context.add_proposals(self, proposals, True)
            except ConnectionRefusedError:
                logger.warning("TAG_PROVIDER: connection to the scholastica application "
                          "refused, most likely because it is not currently running")
    
    def do_get_name(self):
        return "scholastica"
                    
    def get_filtered_proposals(self, words, prefix):
        proposals = [word for word in words if word.startswith(prefix) and word != prefix]
        return proposals
