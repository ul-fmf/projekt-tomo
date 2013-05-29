#!/usr/bin/env python
import os, site, sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings.local")
    site.addsitedir("/Users/matija/Work/projekt-tomo/virtualenv/lib/python2.7/site-packages")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
