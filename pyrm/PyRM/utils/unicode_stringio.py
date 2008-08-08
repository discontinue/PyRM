
from django.conf import settings
from django.utils.encoding import force_unicode, smart_str

class UnicodeStringIO(object):
    """
    Minimalistic StringIO-file-like object.
    """
    def __init__(self):
        self._container = []

    def write(self, content):
        """
        Append a new chunk.
        Encode unicode to the default charset.
        """
        content = smart_str(content, errors='replace')
        self._container.append(content)

    def getvalue(self):
        """
        Get all content.
        """
        content = ''.join(self._container)
        return content

    def isatty(self):
        """
        Used for the _install section: Redirected the syncdb command.
        It checks sys.stdout.isatty() in django.core.management.color
        """
        return False