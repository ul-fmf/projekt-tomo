import StringIO
import zipfile
from django.http import HttpResponse


def plain_text(name, contents, content_type='text/plain'):
    """
    Downloads a plain text file with the given name and contents.
    """
    response = HttpResponse(content_type='{0}; charset=utf-8'.format(content_type))
    response['Content-Disposition'] = 'attachment; filename={0}'.format(name)
    response.write(contents)
    return response


def zip_archive(archive_name, files):
    """
    Downloads a zip archive with the given name and containing the given
    iterable of files, each represented by a pair, where the first component
    gives the filename and the second one gives the contents.
    """
    string_buffer = StringIO.StringIO()
    archive = zipfile.ZipFile(string_buffer, 'w', zipfile.ZIP_DEFLATED)
    for filename, contents in files:
        archive.writestr(filename, contents.encode('utf-8'))
    archive.close()
    response = HttpResponse(string_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename={0}.zip'.format(archive_name)
    return response
