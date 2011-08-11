# coding: utf-8

import os
import logging

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.template.context import RequestContext
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from xhtml2pdf.document import pisaDocument

from pyrm.models.rechnung import Rechnung


def fetch_resources(uri, rel):
    """
    https://github.com/chrisglass/xhtml2pdf/issues/21
    """
#    print "_"*79
#    print "pisa resource:"
#    print "uri:", uri
#    print "rel:", rel

    url_prefix = settings.MEDIA_URL
    if not uri.startswith(url_prefix):
        msg = "uri %r doesn't starts with %r" % (uri, url_prefix)
        print "***", msg
        raise AssertionError(msg)

    url = uri[len(url_prefix):]
#    print "url:", url

    path = os.path.join(settings.MEDIA_ROOT, url)
    if not os.path.exists(path):
        msg = "File %r for uri %r doesn't exists!" % (path, uri)
        print "***", msg
        raise AssertionError(msg)

#    print "path:", path
#    print "-"*79
    return path


def rechnung_drucken(request, pk):
    rechnung = get_object_or_404(Rechnung, pk=pk)
    context = {
        "rechnung": rechnung,
        "is_copy": "is_copy" in request.GET,
    }

    html = render_to_string("pyrm/html_print/rechnung.html", context,
        context_instance=RequestContext(request)
    )

    if "html" in request.GET:
        return HttpResponse(html)

    result = StringIO()

    #log = logging.getLogger("xhtml2pdf")
    pdf = pisaDocument(
        StringIO(html.encode("UTF-8")),
        dest=result,
        link_callback=fetch_resources
    )
    if pdf.err:
        response = HttpResponse(pdf.err, content_type="text/plain")
    else:
        response = HttpResponse(result.getvalue(), mimetype='application/pdf')
        filename = "rechnung%s.pdf" % rechnung.nummer
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response

