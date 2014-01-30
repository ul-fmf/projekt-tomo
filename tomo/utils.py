# -*- coding: utf-8 -*-
import hashlib, json, os

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render_to_response, redirect, render
from django.template import loader, Context, RequestContext
from django.views.decorators.csrf import csrf_exempt

from tomo.utils import *
from tomo.models import *

import tempfile, zipfile

from django.core.exceptions import PermissionDenied
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse



def verify(cond):
    if not cond: raise PermissionDenied
def sign(text):
    return hashlib.md5(text + settings.SECRET_KEY).hexdigest()
def pack(data):
    text = json.dumps(data)
    return (text, sign(text))
def unpack(text, sig):
    verify(sign(text) == sig)
    return json.loads(text)

def plain_text(name, contents, mimetype='text/plain'):
    """
    Returns a response that downloads a plain text file with the given name and
    contents.
    """
    response = HttpResponse(mimetype='{0}; charset=utf-8'.format(mimetype))
    response['Content-Disposition'] = 'attachment; filename={0}'.format(name)
    response.write(contents)
    return response

def zip_archive(name, files):
    """
    Returns a response that downloads a zip archive with the given name and
    containing the given iterable of files, each represented by a pair, where
    the first component gives the name and the second one gives the contents.
    """
    temp = tempfile.TemporaryFile()
    archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
    for n, contents in files:
        archive.writestr(n, contents)
    archive.close()
    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = \
        'attachment; filename={0}.zip'.format(name)
    response['Content-Length'] = temp.tell()
    temp.seek(0)
    return response
