FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install google-cloud-tasks google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client Flask

EXPOSE 8080
CMD ["python", "app.py"]

