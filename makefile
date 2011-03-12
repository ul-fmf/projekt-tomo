default:
	./manage.py runserver

sync:
	touch database
	rm database
	./manage.py syncdb --noinput
	./manage.py loaddata fixtures/*.json

.PHONY: default sync
