# -*- coding: utf-8 -*-
import hashlib
import io
import json
import tempfile
import zipfile
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse

 
def verify(cond):
    if not cond:
        raise PermissionDenied


def sign(text):
    return hashlib.md5(text + settings.SECRET_KEY).hexdigest()


def pack(data):
    text = json.dumps(data)
    return (text, sign(text))


def unpack(text, sig):
    verify(sign(text) == sig)
    return json.loads(text)


def plain_text(name, contents, content_type='text/plain'):
    """
    Returns a response that downloads a plain text file with the given name and
    contents.
    """
    response = HttpResponse(content_type='{0}; charset=utf-8'.format(content_type))
    response['Content-Disposition'] = 'attachment; filename={0}'.format(name)
    response.write(contents)
    return response


def zip_archive(name, files):
    """
    Returns a response that downloads a zip archive with the given name and
    containing the given iterable of files, each represented by a pair, where
    the first component gives the name and the second one gives the contents.
    """
    temp = io.BytesIO()
    archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
    for n, contents in files:
        archive.writestr(n, contents.encode('utf-8'))
    archive.close()
    response = HttpResponse(temp.getvalue(), content_type="application/x-zip-compressed")
    response['Content-Disposition'] = 'attachment; filename={0}.zip'.format(name)
    return response

