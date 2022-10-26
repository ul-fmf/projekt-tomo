from django.urls.converters import IntConverter


class TrueIntConverter(IntConverter):
    """Django URL converter that also accepts negative integers."""

    regex = r"-?\d+"
