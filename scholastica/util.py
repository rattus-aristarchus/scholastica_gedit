from urllib.parse import unquote
from urllib.parse import urlparse
import platform
import logging
import conf

logging.basicConfig(filename=conf.LOGS_FILE,
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_phrase(piter):
    a = piter.copy()
    b = piter.copy()

    while True:
        if a.starts_line():
            break

        a.backward_char()
        ch = a.get_char()

        if not (ch.isalnum() or ch in "_:.-><\"'$%^&?*=+" or ch.isspace()):
            a.forward_char()
            break

    word = a.get_visible_text(b)
    if word[0].isspace():
        word = word[1:]
    return word


def get_word(piter):
    a = piter.copy()
    b = piter.copy()
    
    while True:
        if a.starts_line():
            break
        
        a.backward_char()
        ch = a.get_char()
        
        if not (ch.isalnum() or ch in "_:.,-><\"';$%^&?*=+"):
            a.forward_char()
            break
    
    word = a.get_visible_text(b)
    return word


def get_line(piter):    
    a = piter.copy()
    b = piter.copy()
    
    while True:
        if a.starts_line():
            break
        
        a.backward_char()
    
    line = a.get_visible_text(b)
    return line


def enclosed_line(line):
    if len(line) == 0:
        return False
    for ch in line:
        if ch == " ":
            continue
        if ch == "(" or ch == "[":
            return True
        else:
            return False


def document_path(document):
    location = document.get_file().get_location()
    uri = location.get_uri()
    path = urlparse(uri).path
    if "%" in path:
        path = unquote(path)
    # i've got no idea how or why but on windows the path
    # sometimes starts with a slash
    if path[0] == "/" and platform.system() == "Windows":
        path = path[1:]
    return path


def truncate_source(source):
    """
    Return a short reference to a source from its full name
    """
    result = ""
    
    #The first word of the reference is usually the first word of the source
    for ch in source:
        if ch.isspace() or ch in [",", ":", "."]:
            break
        else:
            result += ch
    
    #After that, usually the year of publishing is added. To find that, we look for 
    #4 consecutive digits that have non-digits on either side
    if len(source) >= 4:
        year = ""  
        for idx in range(len(source) - 3):
            four_consecutive_digits = source[idx:idx+4].isdigit()
            non_digit_before = idx == 0 or not source[idx-1].isdigit()
            non_digit_after = idx+4 >= len(source) or not source[idx+4].isdigit()
            if four_consecutive_digits and non_digit_before and non_digit_after:
                year = source[idx:idx+4]
        if not year == "":
            result += " " + year
    return result
