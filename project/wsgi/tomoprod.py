"""
WSGI config for projekt-tomo.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
and
http://blog.dscpl.com.au/2012/10/requests-running-in-wrong-django.html
"""

import os
os.environ["DJANGO_SETTINGS_MODULE"] = "project.settings.tomoprod"

import sys, site
base_path = "/srv/tomoprod"
ALLDIRS = [base_path, os.path.join(base_path, "virtualenv/lib/python2.6/site-packages")]

# Remember original sys.path.
prev_sys_path = list(sys.path) 

# Add each new site-packages directory.
for directory in ALLDIRS:
  site.addsitedir(directory)

# Reorder sys.path so new directories at the front.
new_sys_path = [] 
for item in list(sys.path): 
    if item not in prev_sys_path: 
        new_sys_path.append(item) 
        sys.path.remove(item) 
sys.path[:0] = new_sys_path 

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
