import tempfile, zipfile

from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse


def plain_text(name, contents):
    """
    Returns a response that downloads a plain text file with the given name and
    contents.
    """
    response = HttpResponse(mimetype='text/plain; charset=utf-8')
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

