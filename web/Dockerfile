FROM python:3.7
ENV PYTHONUNBUFFERED=1
WORKDIR /src
RUN groupadd -g 1000 tomo && useradd -m -u 1000 -g tomo tomo -s /bin/bash
COPY requirements /src/requirements
RUN pip install --no-cache-dir -r requirements/arnes.txt
COPY . /src/
RUN mkdir -p /var/static
RUN chown -R tomo /src /var/static
USER tomo
ENV UWSGI_CHDIR=/src
ENV UWSGI_MODULE=web.wsgi.arnes:application
ENV UWSGI_MASTER=True
# Enables us to simply restart UWSGI by deleting /tmp/project-master.pid
ENV UWSGI_PIDFILE=/tmp/project-master.pid
ENV UWSGI_VACUUM=True
ENV UWSGI_MAX_REQUESTS=5000
ENV UWSGI_UID=tomo
ENV UWSGI_GID=tomo
ENV UWSGI_HTTP=:8080
ENV UWSGI_STATIC_MAP=/static=/var/static
CMD ./manage.py migrate --no-input && ./manage.py collectstatic --no-input && uwsgi
