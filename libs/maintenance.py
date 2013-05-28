def maintenance(application, lock, message):
    if os.path.exists(lock):
        return application
    else:
        def maintenance_wsgi_application(environ, start_response):
            start_response('503 Service Unavailable',
                           [('Content-Type', 'text/html; charset=UTF-8')])
            with open(message) as f:
                return [f.read()]
        return maintenance_wsgi_application
