# Architecture Overview

1. Trigger
  ** A file enters the designated inbox folder in Google Drive.
  ** Google Drive Push Notification is sent to Cloud Pub/Sub.

2. Event Handling:

  ** Cloud Run listens to Pub/Sub events and initiates the workflow.
  ** Extracted metadata is analyzed to determine the workflow type (e.g., Invoice, Homeowner Request).

3. Workflow Automation:

  ** Google Cloud Tasks schedules the workflow steps.
  ** Tasks include:
    *** Updating a Google Sheet (e.g., logging an invoice).
    *** Scheduling calendar events (e.g., payment reminders).
    *** Sending email notifications (using Gmail API).

4. Orchestration and Status Tracking:

  ** Workflow status and history are maintained in Google Sheets.


# Prerequisites

## Development tools

Ensure you have the following installed:

* Python 3.9
* Google Cloud SDK (gcloud command)
* Google Apps Script (clasp)
* Ngrok (for local development with OAuth)

## Google Cloud project

Go to console.cloud.google.com and create a new Google Cloud project.

Enable the following APIs:

* Google Cloud Tasks API
* Google Drive API
* Google Docs API
* Google Sheets API
* Google Vision API
* Google Vision AI API
* Gmail API

Create OAuth 2.0 Client Credentials (under APIs & Services > Credentials).
Hang on to the `client_secrets.json` file.

Create a secret in Secret Manager:
```
  gcloud secrets create domifile-oauth-tokens --replication-policy="automatic"
```

Create a service account and configure IAM roles:
* roles/cloudtasks.enqueuer
* roles/drive.reader
* roles/sheets.editor
* roles/calendar.admin

# Setting Up API Server

The API server...

* Is implemented based on Flask.
* Manages subscriptions and installations.
* Implements a webhook for notification of incoming documents.

To set up the API server (MacOS only):

* Install Xcode Command Line Tools, including "make"

* `cd server`

* Create a virtual environment

* Run make.  Correct any errors that prevent all packages from being loaded.

* Create `.env` by copying `env.example` and editing the file to reflect your settings.

* Run the server

```
flask run
```

Your API will be running on http://127.0.0.1:5000/.

# Frontend (Google Apps Script UI Extension)

* Open Google Drive.
* Click New > More > Google Apps Script.
* Replace Code.gs with the contents of `frontend/code.gs`
* Save and deploy as an add-on.

# Local Testing (Ngrok for OAuth)

To test OAuth authentication, expose your local Flask server using ngrok:

```
ngrok http 5000
```

Copy the generated HTTPS forwarding URL and update your OAuth redirect URI in Google Cloud Console.

# Deploying to Google Cloud

Once tested locally, deploy using Google Cloud Run:

```
gcloud auth login
gcloud config set project your_project_id
gcloud run deploy domofile --source . --platform managed --allow-unauthenticated
```

Your API will be available via a public URL.
