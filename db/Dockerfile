FROM mongo

COPY ./dump /tmp/dump/air_quality

COPY ./import_data.sh /docker-entrypoint-initdb.d/import_data.sh

RUN chmod +x /docker-entrypoint-initdb.d/import_data.sh
