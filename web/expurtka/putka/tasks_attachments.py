import mimetypes
import os

import expurtka.putka.config.settings as settings
from django.http import HttpResponse, HttpResponseServerError
from django.utils.html import format_html

PUBLIC_TYPES = (
    settings.ATT_TYPE.image,
    settings.ATT_TYPE.inout_public,
    settings.ATT_TYPE.generic_public,
)
TEXT_TYPES = (settings.ATT_TYPE.inout_public, settings.ATT_TYPE.inout_secret)
EXTENSIONS_FOR_TYPE = {
    settings.ATT_TYPE.image: ".bmp .jpg .jpeg .gif .png .tiff",
    settings.ATT_TYPE.generic_public: ".pdf",
    settings.ATT_TYPE.inout_secret: ".in .out",
    settings.ATT_TYPE.inout_public: ".pubin .pubout",
}
TYPE_ASSOCIATIONS = {}
for type, exts in EXTENSIONS_FOR_TYPE.items():
    for ext in exts.split():
        TYPE_ASSOCIATIONS[ext] = type


def guess_att_type(filename):
    """Return the attachment type based on the file extension."""
    return TYPE_ASSOCIATIONS.get(
        os.path.splitext(filename)[1], settings.ATT_TYPE.generic_secret
    )


def compute_preview(att, preview_mode):
    """Return preview of attachment `att`, that has already been permission checked.

    If `preview_mode` is 'plain', the file is sent as (truncated) text/plain or an image.
    If `preview_mode` is 'hex', a (truncated) hex dump of the file is sent.
    """
    data = bytes(att.data)
    mime_type = (
        mimetypes.guess_type(att.filename, strict=False)[0]
        or "application/octet-stream"
    )
    PREVIEW_SIZE = 20000  # truncate at this many bytes

    if preview_mode == "plain":
        if att.type == settings.ATT_TYPE.image:
            return HttpResponse(data, content_type=mime_type)
        else:
            if len(data) > PREVIEW_SIZE:
                data = (
                    data[: PREVIEW_SIZE // 2]
                    + b"\n[ ... truncated ... ]\n"
                    + data[-PREVIEW_SIZE // 2 :]
                    + b"\n[ NOTE: truncated in the middle ]"
                )
            html = format_html("<pre>{}</pre>", data.decode("utf-8", "replace"))
            return HttpResponse(
                html, content_type="text/html"
            )  # text/plain forces download if weird characters are present in the response
    elif preview_mode == "hex":
        L = 16  # this many bytes per line of hex dump
        n = PREVIEW_SIZE // 4 // 2 // L * L  # 1 byte raw data == cca 4 bytes hex dump
        if len(data) > 2 * n:
            data = (
                hex_dump(data[:n], L)
                + "\n[ ... truncated ... ]\n"
                + hex_dump(data[-n:], L)
                + "\n[ NOTE: truncated in the middle ]"
            )
        else:
            data = hex_dump(data, L)
        return HttpResponse(data, content_type="text/plain")
    else:
        return HttpResponseServerError("Unsupported preview mode.")


def hex_dump(data: bytes, line_len=8):
    """Return a nicely readable hex dump of `data`; each line contains `line_len` original bytes."""
    dump = []
    group_size = 4
    for start in range(0, len(data), line_len):
        byte_slice = data[start : start + line_len]
        s = len(byte_slice)

        hex_bytes = "".join(
            "{:02x}{}".format(
                byte_slice[i],
                " | " if (i + 1) % group_size == 0 and i != line_len - 1 else " ",
            )
            for i in range(s)
        )
        align_chars = (
            "   " * (line_len - s) + "  " * ((line_len - s) // group_size) + ":: "
        )
        text = []
        for i in range(s):
            text.append(chr(byte_slice[i]) if 32 <= byte_slice[i] <= 126 else ".")
            if (i + 1) % group_size == 0 and i != line_len - 1:
                text.append(" ")

        dump.append(hex_bytes + align_chars + "".join(text))
    return "\n".join(dump)


def unixify_newlines(data: bytes):
    """Replace all CRLF and standalone CR with LF."""
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
