FROM python:3.7
ENV PYTHONUNBUFFERED=1
WORKDIR /src
RUN groupadd -g 1000 tomo && useradd -m -u 1000 -g tomo tomo -s /bin/bash
COPY requirements /src/requirements
RUN pip install --no-cache-dir -r requirements/arnes.txt
COPY . /src/
RUN chown -R tomo /src
USER tomo
CMD ["/src/entrypoint.sh"]