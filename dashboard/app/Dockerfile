# stage 1
FROM python:3.10-slim as install-requirements
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# stage 2
FROM install-requirements
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./
FROM install-requirements
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:server

